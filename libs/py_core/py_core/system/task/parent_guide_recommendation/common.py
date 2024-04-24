from typing import TypeAlias

from pydantic import BaseModel

from py_core.system.guide_categories import DialogueInspectionCategory
from py_core.system.model import ParentGuideElement

ParentGuideRecommendationAPIResult: TypeAlias = list[ParentGuideElement]


class DialogueInspectionResult(BaseModel):
    categories: list[DialogueInspectionCategory]
    rationale: str | None = None
    feedback: str | None = None
