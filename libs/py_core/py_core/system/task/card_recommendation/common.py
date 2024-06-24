from pydantic import BaseModel, ConfigDict, conset, validator
from py_core.utils.default_cards import DEFAULT_EMOTION_LABELS


class ChildCardRecommendationAPIResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    topics: set[str] = conset(item_type=str, min_length=4, max_length=4)
    actions: set[str] = conset(item_type=str, min_length=4, max_length=4)
    emotions: set[str] = conset(item_type=str, min_length=4, max_length=4)

    @validator('emotions')
    @classmethod
    def check_emotion_types(cls, v: list[str]):
        if not all(keyword.lower().strip() in DEFAULT_EMOTION_LABELS for keyword in v):
            raise ValueError("emotion keywords must be one of the default emotion card set.")
        else:
            return v