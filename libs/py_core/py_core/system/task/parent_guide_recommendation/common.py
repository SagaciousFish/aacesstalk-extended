from enum import StrEnum
from typing import TypeAlias

from pydantic import BaseModel

from py_core.system.model import ParentGuideElement

ParentGuideRecommendationAPIResult: TypeAlias = list[ParentGuideElement]


class DialogueInspectionWarningType(StrEnum):
    Blame="blame"
    Correction="correction"
    Complex="complex"
    Deviation="deviation"
    Neutral="neutral"

class DialogueInspectionElement(BaseModel):
    category: DialogueInspectionWarningType
    rationale: str

DialogueInspectionResult: TypeAlias = list[DialogueInspectionElement]
