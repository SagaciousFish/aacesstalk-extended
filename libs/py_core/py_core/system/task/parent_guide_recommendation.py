from typing import TypeAlias

from chatlib.llm.integration.openai_api import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.converter import generate_type_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams

from py_core.system.model import ParentGuideRecommendationResult, Dialogue, ParentGuideElement
from py_core.system.task.stringify import convert_dialogue_to_str

ParentGuideRecommendationAPIResult: TypeAlias = list[ParentGuideElement]

str_output_converter, output_str_converter = generate_type_converter(ParentGuideRecommendationAPIResult)

class ParentGuideRecommendationParams(ChatCompletionFewShotMapperParams):
    pass

class ParentGuideRecommendationGenerator:
    def __init__(self):
        self.__mapper: ChatCompletionFewShotMapper[Dialogue, ParentGuideRecommendationAPIResult, ParentGuideRecommendationParams] = (
            ChatCompletionFewShotMapper(GPTChatCompletionAPI(),
                                        instruction_generator=self.__prompt_generator,
                                        input_str_converter=convert_dialogue_to_str,
                                        output_str_converter=output_str_converter,
                                        str_output_converter=str_output_converter
                                        ))

    @staticmethod
    def __prompt_generator(input: Dialogue, params: ParentGuideRecommendationParams) -> str:
        prompt = """
You are a helpful assistant who help a communication between children using Alternative Augmented Communication tools and their parents.
Suppose that you are helping a communication with a minimally verbal autistic child and parents in Korean.
Given the last message of the children, suggest a list of sentences that can help the parents pick to respond or ask questions.

Return a JSON object in the following format:
Array<{
        "example": Provide response or question that parents can make to the child's message.
        "guide": Provide guide for parents of autistic children to consider when responding to the child's answer. Keep the guide short and concise so parents can read it quickly and move on.
    }>

The result should be in Korean and please provide up to three options for each element.
"""
        return prompt

    async def generate(self, dialogue: Dialogue)->ParentGuideRecommendationResult:
        guide_list: ParentGuideRecommendationAPIResult = await self.__mapper.run(None, dialogue, ParentGuideRecommendationParams(model=ChatGPTModel.GPT_4_0613, api_params={}))
        return ParentGuideRecommendationResult(recommendations=guide_list)
