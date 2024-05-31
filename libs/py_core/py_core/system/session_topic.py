from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SessionTopicCategory(StrEnum):
    Plan="plan"
    Recall="recall"
    Free="free"

    def __init__(self, value):
        self.description={
            "plan": "The dyad shares today's todos or plans.",
            "recall": "The dyad gets to know what the child did on that day.",
            "free": "The dyad converses about a free topic that the child is interested in.",
        }[value]

class SessionTopicInfo(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    category: SessionTopicCategory
    subtopic: Optional[str] = None
    subtopic_description: Optional[str] = None

    def to_readable_description(self):
        if self.subtopic is not None:
            return f"""{self.category.description} Specifically, the conversation is about {self.subtopic} ({self.subtopic_description})."""
        return f"{self.category.description}"
