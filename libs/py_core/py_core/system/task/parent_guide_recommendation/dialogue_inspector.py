from chatlib.tool.converter import generate_type_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams, MapperInputOutputPair
from chatlib.llm.integration import GPTChatCompletionAPI

from py_core.system.model import Dialogue
from py_core.system.task.parent_guide_recommendation.common import DialogueInspectionResult
from py_core.system.task.stringify import convert_dialogue_to_str


class DialogueInspector:

    def __init__(self):

        str_output_converter, output_str_converter = generate_type_converter(DialogueInspectionResult, 'json')

        self.__mapper: ChatCompletionFewShotMapper[Dialogue, DialogueInspectionResult, ChatCompletionFewShotMapperParams] = ChatCompletionFewShotMapper(
            api= GPTChatCompletionAPI(),
            instruction_generator="""
You are a helpful scientist that analyzes a dialogue between a parent and a child with Autism Spectrum Disorder, and identify noteworthy signals from the parent's behavior responding to his/her child.
            """,
            input_str_converter=convert_dialogue_to_str,
            str_output_converter=str_output_converter,
            output_str_converter=output_str_converter
        )

