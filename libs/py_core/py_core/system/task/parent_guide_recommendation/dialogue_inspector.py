from time import perf_counter

from chatlib.tool.converter import generate_pydantic_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams, \
    MapperInputOutputPair
from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel

from py_core.system.model import Dialogue, DialogueMessage, DialogueRole, CardCategory
from py_core.system.task.parent_guide_recommendation.common import DialogueInspectionResult, \
    DialogueInspectionCategory
from py_core.system.task.parent_guide_recommendation.guide_translator import GuideTranslator
from py_core.system.task.stringify import DialogueToStrConversionFunction

_EXAMPLES = [
    MapperInputOutputPair(
        input=[
            DialogueMessage.example_parent_message("What did you do at school?"),
            DialogueMessage.example_child_message(("School", CardCategory.Topic), ("Play", CardCategory.Action)),
            DialogueMessage.example_parent_message("I asked you not to play games at school. Didn't I?")
        ],
        output=DialogueInspectionResult(categories=[DialogueInspectionCategory.Correction], rationale="The parent is about to scold the child not to play games.", feedback="You seem to be scolding him before obtaining to more concrete information. Please gather more information before judgment.")
    )
]

class DialogueInspector:

    def __init__(self):

        str_output_converter, output_str_converter = generate_pydantic_converter(DialogueInspectionResult, 'json')

        self.__mapper: ChatCompletionFewShotMapper[
            Dialogue, DialogueInspectionResult, ChatCompletionFewShotMapperParams] = ChatCompletionFewShotMapper(
            api=GPTChatCompletionAPI(),
            instruction_generator="""

- Role: You are a helpful communication expert that analyzes a conversation pattern between a parent and a autistic child, and identify noteworthy signals from the parent's behavior responding to his/her child.
- Task: Given a dialogue, inspect the last parent message.

[Input format]
The dialogue will be formatted as an XML.
The last message of the parent to be inspected is marked with an attribute 'inspect="true"'.

[Output format]
- The inspection result would be a JSON object formatted as the following:
{
  "categories": string[] // Inspected categories as part of the predefined inspection categories in [Inspection categories].
  "rationale": string // Rationale for assigning these inspection categories.
  "feedback": string // Provide a message to parents to let them know the current conversation status
}

[Inspection categories]
"blame": When the parent criticizes or negatively evaluates the child's respons, like reprimanding or scolding
"correction": When the parent is compulsively correcting the child's response or pointing out that the child is wrong.
"complex": When a parent's dialogue contains more than one goal or intent.
"deviation": When both parent and child stray from the main topic of the conversation.
"neutral": General conversation that does not fit into the other status categories.


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

    async def inspect(self, dialogue: Dialogue, task_id: str)->tuple[DialogueInspectionResult | None, str]:
        t_start = perf_counter()
        if len(dialogue) == 0:
            result = None, task_id
        elif dialogue[len(dialogue) - 1].role != DialogueRole.Parent:
            result = None, task_id
        else:
            result = (await self.__mapper.run(_EXAMPLES, dialogue, ChatCompletionFewShotMapperParams(model=ChatGPTModel.GPT_3_5_0613, api_params={}))), task_id
            if "neutral" in result[0].categories:
                result = None, task_id
        t_end = perf_counter()
        print(f"Dialogue inspection took {t_end - t_start} sec. result: ", result[0], f"task_id: {result[1]}")

        return result
