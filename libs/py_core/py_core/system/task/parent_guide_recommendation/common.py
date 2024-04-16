from enum import StrEnum
from typing import TypeAlias

from pydantic import BaseModel

from py_core.system.model import ParentGuideElement

ParentGuideRecommendationAPIResult: TypeAlias = list[ParentGuideElement]


class DialogueInspectionWarningType(StrEnum):
    KeepAsking="keep_asking"
    Aggressive="aggressive_reaction"
    Reprimanding="reprimanding"
    DoubleBarrelled="double_barrelled"

class DialogueInspectionElement:
    type: DialogueInspectionWarningType
    rationale: str

DialogueInspectionResult: TypeAlias = list[DialogueInspectionElement]
