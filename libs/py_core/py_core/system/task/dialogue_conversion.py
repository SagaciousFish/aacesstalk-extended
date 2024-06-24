from pydantic import BaseModel
from typing import Callable

from py_core.system.model import Dialogue, DialogueRole, DialogueMessage, ParentType
from py_core.system.session_topic import SESSION_TOPIC_CATEGORY_DESC_DICT, SessionTopicInfo


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
    



_dialogue_to_str = DialogueToStrConversionFunction()

class DialogueInput(BaseModel):
    parent_type: ParentType
    topic: SessionTopicInfo
    dialogue: Dialogue

class DialogueInputToStrConversionFunction:
    def __init__(self, include_topic: bool=False, include_parent_type: bool=False):
        self.include_topic = include_topic
        self.include_parent_type = include_parent_type
    
    def __call__(self, input: DialogueInput, params) -> str:
        rows: list[str] = []
        
        if self.include_topic is True:
            subtopic_str = f"<subtopic>{input.topic.subtopic} ({input.topic.subtopic_description})</subtopic>" if input.topic.subtopic is not None else ""
            rows.append(f"<topic><desc>{SESSION_TOPIC_CATEGORY_DESC_DICT[input.topic.category]}</desc>{subtopic_str}</topic>")

        rows.append(_dialogue_to_str(input.dialogue, params))

        if self.include_parent_type:
            rows.append(f"<parent>{input.parent_type}</parent>")


        return "\n".join(rows)