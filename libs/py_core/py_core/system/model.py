from enum import StrEnum
from typing import Literal, TypeAlias
from nanoid import generate

from pydantic import BaseModel, ConfigDict, TypeAdapter, Field


def id_generator() -> str:
    return generate(size=20)


class ChildCardRecommendationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=id_generator)
    nouns: list[str]
    emotions: list[str]
    actions: list[str]


class CardInfo(BaseModel):
    text: str
    category: Literal["noun", "emotion", "action"]

    def simple_str(self) -> str:
        return f"{self.text} ({self.category})"


class ParentGuidanceElement(BaseModel):
    model_config = ConfigDict(frozen=True)

    example: str
    guide: str


class ParentRecommendationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=id_generator)
    recommendations: list[ParentGuidanceElement]


class DialogueRole(StrEnum):
    Parent = "parent"
    Child = "child"


class DialogueMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=id_generator)
    speaker: DialogueRole
    content: str | list[CardInfo]
    recommendation_id: str | None = None


Dialogue: TypeAlias = list[DialogueMessage]

DialogueTypeAdapter = TypeAdapter(Dialogue)
