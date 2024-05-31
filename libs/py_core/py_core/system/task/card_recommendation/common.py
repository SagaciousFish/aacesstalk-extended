from typing import Callable
from chatlib.tool.converter import generate_pydantic_converter
from pydantic import BaseModel, ConfigDict
from py_core.system.model import CardCategory, Dialogue, DialogueMessage, DialogueRole, ParentType

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
    