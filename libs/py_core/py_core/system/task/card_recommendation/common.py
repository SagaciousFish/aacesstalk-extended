from typing import Callable
from chatlib.tool.converter import generate_pydantic_converter
from pydantic import BaseModel, ConfigDict, conlist, validator
import yaml
from py_core.config import AACessTalkConfig
from py_core.system.model import CardCategory, Dialogue, DialogueMessage, DialogueRole, ParentType



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


def load_default_cards(path: str)->list[DefaultCardInfo]:
    with open(path) as f:
       l = yaml.load(f, yaml.SafeLoader)
       return [DefaultCardInfo(**e) for e in l]
    
DEFAULT_EMOTION_CARDS = load_default_cards(AACessTalkConfig.default_emotion_card_table_path)
DEFAULT_EMOTION_LABELS = [c.label.lower().strip() for c in DEFAULT_EMOTION_CARDS]


class ChildCardRecommendationAPIResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    topics: list[str] = conlist(item_type=str, min_length=4, max_length=4, unique_items=True)
    actions: list[str] = conlist(item_type=str, min_length=4, max_length=4, unique_items=True)
    emotions: list[str] = conlist(item_type=str, min_length=4, max_length=4, unique_items=True)

    @validator('emotions')
    @classmethod
    def check_emotion_types(cls, v: list[str]):
        if not all(keyword.lower().strip() in DEFAULT_EMOTION_LABELS for keyword in v):
            raise ValueError("emotion keywords must be one of the default emotion card set.")
        else:
            return v


class DialogueToStrConversionFunction:

    def __init__(self,
                 message_content_formatter: Callable[[DialogueMessage, Dialogue], str] | None = None,
                 message_row_formatter: Callable[[str, DialogueMessage, Dialogue], str] | None = None
                 ):
        self.__message_content_formatter = message_content_formatter or self.message_content_formatter_default
        self.__message_row_formatter = message_row_formatter or self.message_row_formatter_default

    @staticmethod
    def message_content_formatter_default(message: DialogueMessage, dialogue: Dialogue) -> str:
        return f"{'Parent' if message.role == DialogueRole.Parent else 'Child'}: {message.content if isinstance(message.content, str) else ', '.join([card.label for card in message.content])}"

    @staticmethod
    def message_row_formatter_default(formatted: str, message: DialogueMessage, dialogue: Dialogue) -> str:
        return f"\t<msg>{formatted}</msg>"

    def __call__(self, dialogue: Dialogue, params) -> str:
        script = "\n".join(
            [self.__message_row_formatter(self.__message_content_formatter(message, dialogue), message, dialogue) for
             message in dialogue])

        result = f"""
<dialogue>
{script}
</dialogue>"""
        return result