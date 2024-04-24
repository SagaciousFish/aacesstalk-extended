import re

from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams, \
    MapperInputOutputPair
from chatlib.utils.jinja_utils import convert_to_jinja_template
from time import perf_counter

from py_core.config import AACessTalkConfig
from py_core.system.shared import vector_db
from py_core.system.task.parent_guide_recommendation.common import ParentGuideRecommendationAPIResult
from py_core.utils.lookup_translator import LookupTranslator
from py_core.utils.models import DictionaryRow

template = convert_to_jinja_template("""You are a helpful translator who translates an utterance of a parent talking with their child with ASD.
[Task]
- Translate the following English message to Korean.
- Note that the messages are intended to be spoken by parent to a kid.
- Don't use honorific form of Korean.
""")


def _generate_prompt(input, params) -> str:
    r = template.render()
    return r


class ParentExampleMessageTranslator:

    def __init__(self):
        api = GPTChatCompletionAPI()
        api.config().verbose = False

        self.__dictionary = LookupTranslator("parent_examples",
                                             AACessTalkConfig.parent_example_translation_dictionary_path,
                                             vector_db=vector_db,
                                             verbose=True)

        self.__example_translator: ChatCompletionFewShotMapper[str, str, ChatCompletionFewShotMapperParams] = ChatCompletionFewShotMapper.make_str_mapper(api,
                                                                                                     instruction_generator=_generate_prompt)

    async def translate_example(self, original_message: str) -> str:
        t_start = perf_counter()

        samples = self.__dictionary.query_similar_rows(original_message, None, k=3)

        samples_formatted = [
            MapperInputOutputPair(input=sample.english, output=sample.localized) for sample in samples
        ]

        result = await self.__example_translator.run(samples_formatted, original_message, ChatCompletionFewShotMapperParams(
            api_params={}, model=ChatGPTModel.GPT_3_5_0613))

        t_end = perf_counter()

        # print(f"LLM translation took {t_end - t_start} sec.")

        return result
