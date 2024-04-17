from time import perf_counter

from chatlib.llm.integration.openai_api import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.converter import generate_type_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams, \
    MapperInputOutputPair

from py_core.system.model import ParentGuideRecommendationResult, Dialogue, ParentGuideElement, DialogueMessage, \
    CardCategory
from py_core.system.task.parent_guide_recommendation.common import ParentGuideRecommendationAPIResult
from py_core.system.task.parent_guide_recommendation.translator import ParentGuideTranslator
from py_core.system.task.stringify import DialogueToStrConversionFunction


class ParentGuideRecommendationParams(ChatCompletionFewShotMapperParams):
    pass


# Variables for mapper ================================================================================================================

def generate_parent_guideline_prompt(input: Dialogue, params: ParentGuideRecommendationParams) -> str:
    prompt = """
Role: You are a helpful assistant who helps facilitate communication between minimally verbal autistic children and their parents.
Task: Given a dialogue between a parent and a child, suggest a list of guides that can help the parents choose how to respond or ask questions in response to the child's last message.
Note that the child always convey their message through keywords.
Goal of the conversation: To help the child and parent elaborate on a topic together.

[General instructions for parent's guide]
- Provide simple and easy-to-understand sentences consisting of no more than 5-6 words.
- Each guide should contain one purpose or intention.
- Based on the child's last message, select up to three most appropriate directions from the guide directions provided below.
- Each guide should be contextualized based on the child's response and not be too general.

[Parent guide categories]
"intention": Check the intention behind the child’s response and ask back.
"specification": Ask about "what" to specify the event.
"clues": Give clues that can be answered based on previously known information.
"wordplay": Follow the child’s favorite word play.
"coping": Suggest coping strategies for specific situations to the child.
"stimulate": Suggest presenting information that contradicts what is known to stimulate the child's interest.
"share": Suggest sharing the parent's thoughts or feelings in simple language.
"empathize": Suggest empathizing with the child's feelings.
"encourage": Suggest encouraging the child's actions or emotions.

[Response format]
Return a json list with each element formatted as:
{
  "category": The category of "Parent guide category",
  "guide": The guide message provided to the parent.
}

"""
    return prompt


PARENT_GUIDE_EXAMPLES: list[MapperInputOutputPair[Dialogue, ParentGuideRecommendationAPIResult]] = [
    MapperInputOutputPair(
        input=[
            DialogueMessage.example_parent_message("Did you remember that we will visit granma today?"),
            DialogueMessage.example_child_message(("Grandma", CardCategory.Topic), ("Play", CardCategory.Action))
        ],
        output=[
            ParentGuideElement(
                category="empathize",
                guide="Repeat that your kid wants to play with grandma."
            ),
            ParentGuideElement(
                category="encourage",
                guide="Suggest things that the kid can do with grandma playing."
            ),
            ParentGuideElement(
                category="specification",
                guide="Ask about what your kid wants to do playing."
            ),
        ]
    ),
    MapperInputOutputPair(
        input=[
            DialogueMessage.example_parent_message("How was your day at kinder?"),
            DialogueMessage.example_child_message(
                ("Kinder", CardCategory.Topic),
                ("Friend", CardCategory.Topic),
                ("Tough", CardCategory.Emotion)),
        ],
        output=[
            ParentGuideElement(
                category="empathize",
                guide="Empathize that the kid had tough time due to a friend."
            ),
            ParentGuideElement(
                category="intention",
                guide="Check whether the kid had tough time with the friend."
            ),
            ParentGuideElement(
                category="specification",
                guide="Ask what was tough with the friend."
            ),
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
            Dialogue, ParentGuideRecommendationAPIResult, ParentGuideRecommendationParams] = ChatCompletionFewShotMapper(
            api,
            instruction_generator=generate_parent_guideline_prompt,
            input_str_converter=DialogueToStrConversionFunction(),
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
