from enum import StrEnum
from typing import TypeAlias, Optional

from chatlib.utils.time import get_timestamp
from nanoid import generate
from pydantic import BaseModel, ConfigDict, TypeAdapter, Field


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
    model_config = ConfigDict(frozen=True)

    text: str = Field()
    localized: str
    category: CardCategory

    def simple_str(self) -> str:
        return f"{self.localized} ({self.text}) | {self.category}"


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
    model_config = ConfigDict(frozen=True)

    category: str | None
    guide: str
    guide_localized: Optional[str] =None
    type: ParentGuideType = ParentGuideType.Messaging

    def with_guide_localized(self, localized: str) -> 'ParentGuideElement':
        return self.model_copy(update=dict(guide_localized=localized))

    @classmethod
    def messaging_guide(cls, category: str, guide: str) -> 'ParentGuideElement':
        return ParentGuideElement(category=category, guide=guide, type=ParentGuideType.Messaging)

    @classmethod
    def feedback(cls, category: str | None, guide: str) -> 'ParentGuideElement':
        return ParentGuideElement(category=category, guide=guide, type=ParentGuideType.Feedback)


class ParentGuideRecommendationResult(ModelWithIdAndTimestamp):
    model_config = ConfigDict(frozen=True)

    recommendations: list[ParentGuideElement]


class DialogueRole(StrEnum):
    Parent = "parent"
    Child = "child"


class DialogueMessage(ModelWithIdAndTimestamp):
    model_config = ConfigDict(frozen=True)

    role: DialogueRole
    content: str | list[CardInfo]
    content_en: str | None = None
    recommendation_id: str | None = None

    @classmethod
    def example_parent_message(cls, content_en: str) -> 'DialogueMessage':
        return DialogueMessage(content="_", content_en=content_en, role=DialogueRole.Parent)

    @classmethod
    def example_child_message(cls, *card_labels_eng: tuple[str, CardCategory]) -> 'DialogueMessage':
        return DialogueMessage(role=DialogueRole.Child,
                               content=[CardInfo(text=label, localized="", category=category, recommendation_id="") for
                                        label, category in card_labels_eng])


Dialogue: TypeAlias = list[DialogueMessage]

DialogueTypeAdapter = TypeAdapter(Dialogue)

CardInfoListTypeAdapter = TypeAdapter(list[CardInfo])
