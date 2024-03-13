from enum import StrEnum
from typing import Literal, TypeAlias
from nanoid import generate

from pydantic import BaseModel, ConfigDict, TypeAdapter, Field


class ChildCardRecommendationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    nouns: list[str]
    emotions: list[str]
    actions: list[str]


class ParentGuidanceElement(BaseModel):
    model_config = ConfigDict(frozen=True)

    example: str
    guidance: str


class ParentRecommendationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    recommendations: list[ParentGuidanceElement]


class DialogueRole(StrEnum):
    Parent = "parent"
    Child = "child"


class DialogueMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=lambda: generate(size=20))
    speaker: DialogueRole
    content: str | list[str]
    recommendation_id: str | None = None

Dialogue: TypeAlias = list[DialogueMessage]

DialogueTypeAdapter = TypeAdapter(Dialogue)
