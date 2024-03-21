from chatlib.tool.converter import generate_pydantic_converter
from pydantic import BaseModel, ConfigDict


class ChildCardRecommendationAPIResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    topics: list[str]
    actions: list[str]
    emotions: list[str]

