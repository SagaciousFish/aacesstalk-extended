from enum import StrEnum, auto
from functools import cached_property
from typing import TypeAlias, Optional

from py_core.system.session_topic import SessionTopicInfo
from chatlib.utils.time import get_timestamp
from nanoid import generate
from pydantic import BaseModel, ConfigDict, TypeAdapter, Field

from py_core.system.guide_categories import ParentGuideCategory, DialogueInspectionCategory


def id_generator() -> str:
    return generate(size=20)


class ModelWithId(BaseModel):
    id: str = Field(default_factory=id_generator)


class ModelWithIdAndTimestamp(ModelWithId):
    timestamp: int = Field(default_factory=get_timestamp)

class ModelWithTurnId(BaseModel):
    turn_id: str


class ParentType(StrEnum):
    Mother="mother"
    Father="father"

class Dyad(ModelWithId):
    alias: str = Field(min_length=1, unique=True)
    child_name: str = Field(min_length=1)
    parent_type: ParentType = Field(nullable=False)


class Session(ModelWithId):

    topic: SessionTopicInfo

    local_timezone: str
    started_timestamp: int = Field(default_factory=get_timestamp, index=True)
    ended_timestamp: int | None = Field(default=None, index=True)


class InteractionType(StrEnum):
    SubmitParentMessage = auto()
    RequestParentExampleMessage = auto()
    RefreshChildCards = auto()
    AppendChildCard = auto()
    RemoveLastChildCard = auto()
    ConfirmChildCardSelection = auto()


class Interaction(ModelWithIdAndTimestamp):
    type: InteractionType = Field(nullable=False)
    turn_id: str = Field(nullable=False)
    metadata: dict[str, dict | int | float | str | None]


class CardIdentity(ModelWithId):
    model_config = ConfigDict(frozen=True)

    recommendation_id: str


class CardCategory(StrEnum):
    Topic = "topic"
    Emotion = "emotion"
    Action = "action"
    Core="core"


class CardInfo(CardIdentity):
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    label: str = Field()
    label_localized: str
    category: CardCategory

    def simple_str(self) -> str:
        return f"{self.label_localized} ({self.label}) | {self.category}"


class UserDefinedCardInfo(ModelWithIdAndTimestamp):
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    label: Optional[str] = None
    label_localized: str
    category: CardCategory

    image_filename: Optional[str]
    image_width: Optional[int]
    image_height: Optional[int]


class InterimCardSelection(ModelWithIdAndTimestamp, ModelWithTurnId):
    model_config = ConfigDict(frozen=True)

    cards: list[CardIdentity]


class ChildCardRecommendationResult(ModelWithIdAndTimestamp, ModelWithTurnId):
    model_config = ConfigDict(frozen=True)

    cards: list[CardInfo]

    def find_card_by_id(self, card_id) -> CardInfo | None:
        filtered = [card for card in self.cards if card.id == card_id]
        if len(filtered) > 0:
            return filtered[0]
        else:
            return None


class ParentGuideType(StrEnum):
    Messaging = "messaging"
    Feedback = "feedback"


class ParentGuideElement(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    id: str = Field(default_factory=lambda: generate(size=5))

    category: ParentGuideCategory | list[DialogueInspectionCategory]
    guide: str
    guide_localized: Optional[str] = None
    type: ParentGuideType = ParentGuideType.Messaging

    is_generated: bool = True
    static_guide_key: str | None = None
        

    def with_guide_localized(self, localized: str) -> 'ParentGuideElement':
        return self.model_copy(update=dict(guide_localized=localized))

    @classmethod
    def messaging_guide(cls, category: ParentGuideCategory, guide: str, guide_localized: str | None = None, is_generated: bool = True, static_guide_key: str | None = None) -> 'ParentGuideElement':
        return ParentGuideElement(category=category, guide=guide, type=ParentGuideType.Messaging, guide_localized=guide_localized, is_generated=is_generated, static_guide_key=static_guide_key)

    @classmethod
    def feedback(cls, category: list[DialogueInspectionCategory], guide: str) -> 'ParentGuideElement':
        return ParentGuideElement(category=category, guide=guide, type=ParentGuideType.Feedback)


class ParentGuideRecommendationResult(ModelWithIdAndTimestamp, ModelWithTurnId):
    model_config = ConfigDict(frozen=True)

    guides: list[ParentGuideElement]

    @cached_property
    def messaging_guides(self) -> list[ParentGuideElement]:
        return [guide for guide in self.guides if guide.type == ParentGuideType.Messaging]

    @cached_property
    def feedback_guides(self) -> list[ParentGuideElement]:
        return [guide for guide in self.guides if guide.type == ParentGuideType.Feedback]


class ParentExampleMessage(ModelWithIdAndTimestamp):
    model_config = ConfigDict(frozen=True)

    recommendation_id: str | None = None
    guide_id: str | None = None

    message: str
    message_localized: str | None = None

    
# Dialogue Models =======================================

class DialogueRole(StrEnum):
    Parent = "parent"
    Child = "child"


class DialogueTurn(ModelWithId):
    model_config = ConfigDict(use_enum_values=True)

    session_id: str

    role: DialogueRole

    started_timestamp: int = Field(default_factory=get_timestamp, index=True)
    ended_timestamp: int | None = Field(default=None, index=True)

class DialogueMessage(ModelWithIdAndTimestamp, ModelWithTurnId):
    model_config = ConfigDict(frozen=True)

    role: DialogueRole
    content_localized: str | None = None
    content: str | list[CardInfo]
    turn_id: str | None = None

    @classmethod
    def example_parent_message(cls, content: str) -> 'DialogueMessage':
        return DialogueMessage(content_localized="_", content=content, role=DialogueRole.Parent)

    @classmethod
    def example_child_message(cls, *card_labels_eng: tuple[str, CardCategory]) -> 'DialogueMessage':
        return DialogueMessage(role=DialogueRole.Child,
                               content=[
                                   CardInfo(label=label, label_localized="", category=category, recommendation_id="")
                                   for
                                   label, category in card_labels_eng])


Dialogue: TypeAlias = list[DialogueMessage]

DialogueTypeAdapter = TypeAdapter(Dialogue)

CardInfoListTypeAdapter = TypeAdapter(list[CardInfo])
