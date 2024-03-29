from time import perf_counter

from chatlib.llm.integration.openai_api import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.converter import generate_type_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams, \
    MapperInputOutputPair

from py_core.system.model import ParentGuideRecommendationResult, Dialogue, ParentGuideElement, DialogueMessage, \
    DialogueRole, CardInfo, CardCategory
from py_core.system.task.parent_guide_recommendation.common import ParentGuideRecommendationAPIResult
from py_core.system.task.parent_guide_recommendation.translator import ParentGuideTranslator
from py_core.system.task.stringify import convert_dialogue_to_str



class ParentGuideRecommendationParams(ChatCompletionFewShotMapperParams):
    pass


# Variables for mapper ================================================================================================================

def generate_parent_guideline_prompt(input: Dialogue, params: ParentGuideRecommendationParams) -> str:
    prompt = """
You are a helpful assistant who help a communication between children and their parents.
Suppose that you are helping a communication with a minimally verbal autistic child and parents.
Given the last message of the children, suggest a list of sentences that can help the parents pick to respond or ask questions.

Return an YAML list containing objects with the following attributes:

example: Provide response or question that parents can make to the child's message in English.
guide: Provide guide for parents of autistic children to consider when responding to the child's answer. Keep the guide short and concise so parents can read it quickly and move on.


Please provide up to three options.
"""
    return prompt


PARENT_GUIDE_EXAMPLES: list[MapperInputOutputPair[Dialogue, ParentGuideRecommendationAPIResult]] = [
    MapperInputOutputPair(
        input=[
            DialogueMessage(role=DialogueRole.Parent, content="What did you do at school?"),
            DialogueMessage(role=DialogueRole.Child, content=[
                CardInfo(text="Friend", localized="친구", category=CardCategory.Topic, recommendation_id=""),
                CardInfo(text="Lunch", localized="점심", category=CardCategory.Topic, recommendation_id=""),
                CardInfo(text="Delicious", localized="맛있어요", category=CardCategory.Emotion, recommendation_id=""),
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

# Generator ==========================================
class ParentGuideRecommendationGenerator:
    __MAPPER_PARAMS__ = ParentGuideRecommendationParams(
        model=ChatGPTModel.GPT_4_0613,
        api_params={})

    def __init__(self):
        str_output_converter, output_str_converter = generate_type_converter(ParentGuideRecommendationAPIResult, 'yaml')

        api = GPTChatCompletionAPI()
        api.config().verbose = False

        self.__mapper: ChatCompletionFewShotMapper[
            Dialogue, ParentGuideRecommendationAPIResult, ParentGuideRecommendationParams] = ChatCompletionFewShotMapper(api,
                                        instruction_generator=generate_parent_guideline_prompt,
                                        input_str_converter=convert_dialogue_to_str,
                                        output_str_converter=output_str_converter,
                                        str_output_converter=str_output_converter
                                        )

        self.__translator = ParentGuideTranslator()

    async def generate(self, dialogue: Dialogue) -> ParentGuideRecommendationResult:
        t_start = perf_counter()
        guide_list: ParentGuideRecommendationAPIResult = await self.__mapper.run(PARENT_GUIDE_EXAMPLES, dialogue,
                                                                                 self.__MAPPER_PARAMS__)
        print(guide_list)
        t_trans = perf_counter()
        print(f"Mapping took {t_trans - t_start} sec. Start translation...")
        translated_guide_list: ParentGuideRecommendationAPIResult = await self.__translator.translate(guide_list)
        t_end = perf_counter()
        print(f"Translation took {t_end - t_trans} sec.")
        print(f"Total latency: {t_end - t_start} sec.")
        return ParentGuideRecommendationResult(recommendations=translated_guide_list)

