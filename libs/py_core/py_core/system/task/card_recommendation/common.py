from chatlib.tool.converter import generate_pydantic_converter
from pydantic import BaseModel, ConfigDict
from py_core.system.model import CardCategory, ParentType

class ChildCardRecommendationAPIResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    topics: list[str]
    actions: list[str]


class DefaultCardInfo(BaseModel):
    label: str | dict[ParentType, str]
    label_localized: str | dict[ParentType, str]
    category: CardCategory

    def get_label_for_parent(self, parent_type: ParentType)->str:
        if isinstance(self.label, str):
            return self.label
        else:
            return self.label[parent_type]
    
    def get_label_localized_for_parent(self, parent_type: ParentType)->str:
        if isinstance(self.label_localized, str):
            return self.label_localized
        else:
            return self.label_localized[parent_type]
    