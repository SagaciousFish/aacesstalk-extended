from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class SessionTopicCategory(StrEnum):
    Plan="Plan"
    Recall="Recall"
    Free="Free"

    def __init__(self, value):
        self.description={
            "Plan": "The dyad shares today's todos or plans.",
            "Recall": "The dyad gets to know what the child did on that day",
            "Free": "The dyad converses about a free topic that the child is interested in.",
        }[value]

class SessionTopicInfo(BaseModel):
    category: SessionTopicCategory
    subtopic: Optional[str] = None
    subdescription: Optional[str] = None