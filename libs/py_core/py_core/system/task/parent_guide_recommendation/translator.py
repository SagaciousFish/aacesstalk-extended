import asyncio
import re

import deepl
from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams, \
    MapperInputOutputPair
from chatlib.utils.env_helper import get_env_variable

from py_core.system.model import ParentGuideElement
from py_core.system.task.parent_guide_recommendation.common import ParentGuideRecommendationAPIResult

_EXAMPLE_TRANSLATION_EXAMPLES = [
    MapperInputOutputPair(
        input=[
            "Did you play with the teacher? What type of game was it?",
            "Well done! Are you happy that you finished your game?",
            "So you played a game with your teacher?"
        ],
        output=[
            "선생님이랑 놀았어? 어떤 놀이를 했니?",
            "잘했네! 놀이를 끝까지 마쳐서 행복했니?",
            "선생님과 놀이를 했구나?"
        ]
    ),
    MapperInputOutputPair(
        input=[
            "Did you enjoy your lunch? Can you tell me what you ate?",
            "You had lunch with your friend? That sounds really nice! Can you tell me more about your friend?",
            "You ate together with your friend? What did both of you have for lunch?"
        ],
        output=[
            "점심 맛있게 먹었어? 뭐 먹었는데?",
            "친구랑 점심 먹었어? 너무 좋았겠다! 그 친구에 대해 더 자세히 말해줄래?",
            "친구랑 밥을 같이 먹었구나? 점심으로 뭘 먹었니?"
        ]
    ),
    MapperInputOutputPair(
        input=[
            "That's great! What did you talk about with your teacher?",
            "Which teacher did you talk to? Did it make you happy?",
            "Did you enjoy talking with your teacher?"
        ],
        output=[
            "잘했네! 선생님이랑 무슨 얘기했어?",
            "어떤 선생님이랑 얘기했어? 그래서 기분 어땠니?",
            "선생님이랑 이야기해서 좋았어?"
        ]
    )
]


def convert_messages_to_xml(messages: list[str], params) -> str:
    content = "\n".join([f"  <msg>{msg}</msg>" for msg in messages])
    return f"""<messages>
    {content}
</messages>"""


msg_regex = re.compile(r'<msg>(.*?)</msg>')


def convert_xml_to_messages(xml: str, params) -> list[str]:
    matches = msg_regex.findall(xml)
    return matches


class ParentGuideTranslator:
    __TRANSLATOR_PARAMS__ = ChatCompletionFewShotMapperParams(
        model=ChatGPTModel.GPT_3_5_0613,
        api_params={})

    def __init__(self):
        api = GPTChatCompletionAPI()
        api.config().verbose = False

        self.__example_translator: ChatCompletionFewShotMapper[
            list[str], list[str], ChatCompletionFewShotMapperParams] = ChatCompletionFewShotMapper(api,
                                                                                                   instruction_generator="""
The following XML list contains a list of messages for a parent talking with their child with ASD.
Translate the following messages into Korean.
Note that the messages are intended to be spoken by parent to a kid.
Don't use honorific form of Korean.""",
                                                                                                   input_str_converter=convert_messages_to_xml,
                                                                                                   output_str_converter=convert_messages_to_xml,
                                                                                                   str_output_converter=convert_xml_to_messages
                                                                                                   )

        # Initialize DeepL
        self.__deepl_translator = deepl.Translator(get_env_variable('DEEPL_API_KEY'))


    async def translate(self, api_result: ParentGuideRecommendationAPIResult) -> ParentGuideRecommendationAPIResult:
        examples = [entry.example for entry in api_result]
        guides = [entry.guide for entry in api_result]

        coroutine_translate_examples = self.__example_translator.run(_EXAMPLE_TRANSLATION_EXAMPLES, examples,
                                                                  self.__TRANSLATOR_PARAMS__)
        coroutine_translate_guides = asyncio.to_thread(self.__deepl_translator.translate_text,
                                                             text=guides,
                                                             source_lang="EN",
                                                             target_lang="KO",
                                                             context="The phrases are guides for parents' communication with children with Autism Spectrum Disorder."
                                                             )

        translated_examples, translated_guides = await asyncio.gather(coroutine_translate_examples, coroutine_translate_guides)

        translated_guides = [text_result.text for text_result in translated_guides]

        return [ParentGuideElement(example=example, guide=guide) for example, guide in zip(translated_examples, translated_guides)]
