from enum import StrEnum
from typing import Literal, TypeAlias
from nanoid import generate
from chatlib.utils.time import get_timestamp

from pydantic import BaseModel, ConfigDict, TypeAdapter, Field


def id_generator() -> str:
    return generate(size=20)

class ModelWithIdAndTimestamp(BaseModel):
    id: str = Field(default_factory=id_generator)
    timestamp: int = Field(default_factory=get_timestamp)


class CardInfo(BaseModel):
    text: str
    category: Literal["noun", "emotion", "action"]

    def simple_str(self) -> str:
        return f"{self.text} ({self.category})"

class ChildCardRecommendationResult(ModelWithIdAndTimestamp):
    model_config = ConfigDict(frozen=True)

    nouns: list[str]
    emotions: list[str]
    actions: list[str]

    def get_flatten_cards(self)->list[CardInfo]:
        return [CardInfo(text=noun, category='noun') for noun in self.nouns] + \
            [CardInfo(text=emotion, category='emotion') for emotion in self.emotions] + \
            [CardInfo(text=action, category='action') for action in self.actions]




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
