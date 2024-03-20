from typing import TypeAlias

from chatlib.llm.integration.openai_api import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.converter import generate_type_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams, \
    MapperInputOutputPair

from py_core.system.model import ParentGuideRecommendationResult, Dialogue, ParentGuideElement, DialogueMessage, \
    DialogueRole, CardInfo, CardCategory
from py_core.system.task.stringify import convert_dialogue_to_str

ParentGuideRecommendationAPIResult: TypeAlias = list[ParentGuideElement]

str_output_converter, output_str_converter = generate_type_converter(ParentGuideRecommendationAPIResult)


class ParentGuideRecommendationParams(ChatCompletionFewShotMapperParams):
    pass


PARENT_GUIDE_EXAMPLES: list[MapperInputOutputPair[Dialogue, ParentGuideRecommendationAPIResult]] = [
    MapperInputOutputPair(
        input=[
            DialogueMessage(role=DialogueRole.Parent, content="오늘 학교에서 뭐 했어?"),
            DialogueMessage(role=DialogueRole.Child, content=[
                CardInfo(text="Friend", category=CardCategory.Noun, recommendation_id=""),
                CardInfo(text="Lunch", category=CardCategory.Noun, recommendation_id=""),
                CardInfo(text="Delicious", category=CardCategory.Emotion, recommendation_id=""),
            ]),
        ],
        output=[
            ParentGuideElement(
                example="Glad to hear that you've had delicious lunch! Whom did you eat with?",
                guide="Acknowledge what your child said and ask detailed information."
            ),
            ParentGuideElement(
                example="What did you eat? Which food was delicious?",
                guide="Ask follow-ups to know your kid better. Then you will be able to continue the conversation based on the food that the kid liked."
            )
        ]
    )
]


class ParentGuideRecommendationGenerator:
    def __init__(self):
        self.__mapper: ChatCompletionFewShotMapper[
            Dialogue, ParentGuideRecommendationAPIResult, ParentGuideRecommendationParams] = (
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
        "example": Provide response or question that parents can make to the child's message in English.
        "guide": Provide guide for parents of autistic children to consider when responding to the child's answer. Keep the guide short and concise so parents can read it quickly and move on.
    }>

Please provide up to three options.
"""
        return prompt

    async def generate(self, dialogue: Dialogue) -> ParentGuideRecommendationResult:
        guide_list: ParentGuideRecommendationAPIResult = await self.__mapper.run(PARENT_GUIDE_EXAMPLES, dialogue,
                                                                                 ParentGuideRecommendationParams(
                                                                                     model=ChatGPTModel.GPT_4_0613,
                                                                                     api_params={}))
        return ParentGuideRecommendationResult(recommendations=guide_list)
