from enum import StrEnum
from functools import cache
from typing import TypeAlias, Optional

from pydantic import BaseModel

from py_core.system.model import ParentGuideElement

ParentGuideRecommendationAPIResult: TypeAlias = list[ParentGuideElement]

class CategoryWithDescription(BaseModel):
    label: str
    description: str
    min_turns: Optional[int] = None # Min number of messages in dialogue to activate this category

class DialogueInspectionCategory(StrEnum):
    Blame = "blame"
    Correction = "correction"
    Complex = "complex"
    Deviation = "deviation"

    def __init__(self, value):
        self.description: str = {
            "blame": "When the parent criticizes or negatively evaluates the child's responds, like reprimanding or scolding",
            "correction": "When the parent is compulsively correcting the child's response or pointing out that the child is wrong",
            "complex": "When a parent's dialogue contains more than one goal or intent",
            "deviation": "When both parent and child stray from the main topic of the conversation"
        }[value]

        min_turns_table = {
            "deviation": 5
        }

        self.inspection_min_turns: int | None = min_turns_table[value] if value in min_turns_table else None

    @classmethod
    @cache
    def values_with_desc(cls) -> list[CategoryWithDescription]:
        return list(map(lambda c: CategoryWithDescription(label=c.value, description=c.description, min_turns=c.inspection_min_turns), cls))


class ParentGuideCategory(StrEnum):
    Intention="intention"
    Specification="specification"
    Choice="choice"
    Clues="clues"
    Coping="coping"
    Stimulate="stimulate"
    Share="share"
    Empathize="empathize"
    Encourage="encourage"
    Emotion="emotion"
    Extend="extend"
    Terminate="terminate"

    def __init__(self, value):
        self.description={
            "intention": "Check the intention behind the child’s response and ask back",
            "specification": "Ask about \"what\" to specify the event",
            "choice": "Provide choices for children to select their answers",
            "clues": "Give clues that can be answered based on previously known information",
            "coping": "Suggest coping strategies for specific situations to the child",
            "stimulate": "Present information that contradicts what is known to stimulate the child's interest",
            "share": "Share the parent's emotions and thoughts in simple language",
            "empathize": "Empathize with the child's feelings",
            "encourage": "Encourage the child's actions or emotions",
            "emotion": "Asking about the child's feelings and emotions",
            "extend": "Inducing an expansion or change of the conversation topic",
            "terminate": "Inquiring about the desire to end the conversation"
        }[value]

        min_turns_table = {
            "terminate": 5
        }

        self.active_min_turns: int | None = min_turns_table[value] if value in min_turns_table else None

    @classmethod
    @cache
    def values_with_desc(cls) -> list[CategoryWithDescription]:
        return list(map(lambda c: CategoryWithDescription(label=c.value, description=c.description, min_turns=c.active_min_turns), cls))





class DialogueInspectionResult(BaseModel):
    categories: list[DialogueInspectionCategory]
    rationale: str | None = None
    feedback: str | None = None
