from enum import StrEnum
from typing import Literal, TypeAlias
from functools import cached_property

from nanoid import generate
from chatlib.utils.time import get_timestamp

from pydantic import BaseModel, ConfigDict, TypeAdapter, Field, computed_field


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
    Noun="noun"
    Emotion="emotion"
    Action="action"

class CardInfo(CardIdentity):
    model_config = ConfigDict(frozen=True)

    text: str
    category: CardCategory

    def simple_str(self) -> str:
        return f"{self.text} ({self.category})"

class ChildCardRecommendationResult(ModelWithIdAndTimestamp):
    model_config = ConfigDict(frozen=True)

    nouns: list[str]
    emotions: list[str]
    actions: list[str]

    @computed_field
    @cached_property
    def cards(self)->list[CardInfo]:
        return [CardInfo(text=noun, category=CardCategory.Noun, recommendation_id=self.id) for noun in self.nouns] + \
            [CardInfo(text=emotion, category=CardCategory.Emotion, recommendation_id=self.id) for emotion in self.emotions] + \
            [CardInfo(text=action, category=CardCategory.Action, recommendation_id=self.id) for action in self.actions]

    def find_card_by_id(self, card_id)-> CardInfo | None:
        filtered = [card for card in self.cards if card.id == card_id]
        if len(filtered) > 0:
            return filtered[0]
        else:
            return None


class ParentGuideElement(BaseModel):
    model_config = ConfigDict(frozen=True)

    example: str
    guide: str


class ParentGuideRecommendationResult(ModelWithIdAndTimestamp):
    model_config = ConfigDict(frozen=True)

    recommendations: list[ParentGuideElement]


class DialogueRole(StrEnum):
    Parent = "parent"
    Child = "child"


class DialogueMessage(ModelWithIdAndTimestamp):
    model_config = ConfigDict(frozen=True)

    speaker: DialogueRole
    content: str | list[CardInfo]
    recommendation_id: str | None = None


Dialogue: TypeAlias = list[DialogueMessage]

DialogueTypeAdapter = TypeAdapter(Dialogue)
