from chatlib.tool.converter import generate_type_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams, \
    MapperInputOutputPair
from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel

from py_core.system.model import Dialogue, DialogueMessage, DialogueRole, CardCategory
from py_core.system.task.parent_guide_recommendation.common import DialogueInspectionResult, DialogueInspectionElement, \
    DialogueInspectionWarningType
from py_core.system.task.stringify import DialogueToStrConversionFunction

_EXAMPLES = [
    MapperInputOutputPair(
        input=[
            DialogueMessage.example_parent_message("What did you do at school?"),
            DialogueMessage.example_child_message(("School", CardCategory.Topic), ("Play", CardCategory.Action)),
            DialogueMessage.example_parent_message("I asked you not to play games at school. Didn't I?")
        ],
        output=[DialogueInspectionElement(category=DialogueInspectionWarningType.Schooling, rationale="The parent is about to scold the child not to play games.")]
    )
]

class DialogueInspector:

    def __init__(self):

        str_output_converter, output_str_converter = generate_type_converter(DialogueInspectionResult, 'json')

        self.__mapper: ChatCompletionFewShotMapper[
            Dialogue, DialogueInspectionResult, ChatCompletionFewShotMapperParams] = ChatCompletionFewShotMapper(
            api=GPTChatCompletionAPI(),
            instruction_generator="""
You are a helpful scientist that analyzes a dialogue between a parent and a child with Autism Spectrum Disorder, and identify noteworthy signals from the parent's behavior responding to his/her child.

[Task]
- Given a dialogue, inspect the last parent message.

[Input format]
The dialogue will be formatted as an XML.
The last message of the parent to be inspected is marked with an attribute 'inspect="true"'.

[Output format]
- The inspection result would be a JSON array formatted as the following:
Array<{
  "category": string // One of the predefined inspection category in [Inspection categories].
  "rationale": string // Rationale for assigning this inspection category.
}>
- Return an empty list if no inspection categories are assignable.

[Inspection categories]
- "aggressive": Use this category when the parent is reacting to the child in an aggressive manner, like reprimanding or scolding.
- "schooling": Use this category when the parent is compulsively correcting the child's messages or pointing out that the child is wrong.
            """,
            input_str_converter=DialogueToStrConversionFunction(message_row_formatter=self.__format_dialogue_row),
            str_output_converter=str_output_converter,
            output_str_converter=output_str_converter
        )

    def __format_dialogue_row(self, formatted: str, message: DialogueMessage, dialogue: Dialogue) -> str:
        index = dialogue.index(message)
        if index == len(dialogue) - 1 and message.role == DialogueRole.Parent:
            return f"\t<msg inspect=\"true\">{formatted}</msg>"
        else:
            return DialogueToStrConversionFunction.message_row_formatter_default(formatted, message, dialogue)

    async def inspect(self, dialogue: Dialogue)->DialogueInspectionResult | None:
        if len(dialogue) == 0:
            return None
        elif dialogue[len(dialogue) - 1].role != DialogueRole.Parent:
            return None
        else:
            return await self.__mapper.run(_EXAMPLES, dialogue, ChatCompletionFewShotMapperParams(model=ChatGPTModel.GPT_3_5_0613, api_params={}))
