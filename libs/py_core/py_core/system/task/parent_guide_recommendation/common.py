from enum import StrEnum
from typing import TypeAlias

from pydantic import BaseModel

from py_core.system.model import ParentGuideElement

ParentGuideRecommendationAPIResult: TypeAlias = list[ParentGuideElement]


class DialogueInspectionCategory(StrEnum):
    Blame = "blame"
    Correction = "correction"
    Complex = "complex"
    Deviation = "deviation"
    Neutral = "neutral"


class DialogueInspectionResult(BaseModel):
    categories: list[DialogueInspectionCategory]
    rationale: str
    feedback: str | None = None
