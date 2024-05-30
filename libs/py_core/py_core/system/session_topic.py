from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class SessionTopicCategory(StrEnum):
    Plan="plan"
    Recall="recall"
    Free="free"

    def __init__(self, value):
        self.description={
            "plan": "The dyad shares today's todos or plans.",
            "recall": "The dyad gets to know what the child did on that day",
            "free": "The dyad converses about a free topic that the child is interested in.",
        }[value]

class SessionTopicInfo(BaseModel):
    category: SessionTopicCategory
    subtopic: Optional[str] = None
    subdescription: Optional[str] = None