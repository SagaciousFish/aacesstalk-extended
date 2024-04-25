from enum import StrEnum
from functools import cached_property
from typing import TypeAlias, Optional

from chatlib.utils.time import get_timestamp
from nanoid import generate
from pydantic import BaseModel, ConfigDict, TypeAdapter, Field

from py_core.system.guide_categories import ParentGuideCategory


def id_generator() -> str:
    return generate(size=20)


class ModelWithIdAndTimestamp(BaseModel):
    id: str = Field(default_factory=id_generator)
    timestamp: int = Field(default_factory=get_timestamp)


class CardIdentity(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=id_generator)
    recommendation_id: str


class CardCategory(StrEnum):
    Topic = "topic"
    Emotion = "emotion"
    Action = "action"


class CardInfo(CardIdentity):
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    label: str = Field()
    label_localized: str
    category: CardCategory

    def simple_str(self) -> str:
        return f"{self.label_localized} ({self.label}) | {self.category}"


class ChildCardRecommendationResult(ModelWithIdAndTimestamp):
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

    category: ParentGuideCategory | None
    guide: str
    guide_localized: Optional[str] = None
    type: ParentGuideType = ParentGuideType.Messaging

    def with_guide_localized(self, localized: str) -> 'ParentGuideElement':
        return self.model_copy(update=dict(guide_localized=localized))

    @classmethod
    def messaging_guide(cls, category: ParentGuideCategory, guide: str) -> 'ParentGuideElement':
        return ParentGuideElement(category=category, guide=guide, type=ParentGuideType.Messaging)

    @classmethod
    def feedback(cls, category: ParentGuideCategory | None, guide: str) -> 'ParentGuideElement':
        return ParentGuideElement(category=category, guide=guide, type=ParentGuideType.Feedback)


class ParentGuideRecommendationResult(ModelWithIdAndTimestamp):
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


class DialogueRole(StrEnum):
    Parent = "parent"
    Child = "child"


class DialogueMessage(ModelWithIdAndTimestamp):
    model_config = ConfigDict(frozen=True)

    role: DialogueRole
    content_localized: str | None = None
    content: str | list[CardInfo]
    recommendation_id: str | None = None

    @classmethod
    def example_parent_message(cls, content: str) -> 'DialogueMessage':
        return DialogueMessage(content_localized="_", content=content, role=DialogueRole.Parent)

    @classmethod
    def example_child_message(cls, *card_labels_eng: tuple[str, CardCategory]) -> 'DialogueMessage':
        return DialogueMessage(role=DialogueRole.Child,
                               content=[CardInfo(label=label, label_localized="", category=category, recommendation_id="") for
                                        label, category in card_labels_eng])


Dialogue: TypeAlias = list[DialogueMessage]

DialogueTypeAdapter = TypeAdapter(Dialogue)

CardInfoListTypeAdapter = TypeAdapter(list[CardInfo])
