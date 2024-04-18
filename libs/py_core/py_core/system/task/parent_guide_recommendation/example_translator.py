import asyncio
import re
from time import perf_counter

from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams
from chatlib.utils.jinja_utils import convert_to_jinja_template

from py_core.config import AACessTalkConfig
from py_core.system.model import ParentGuideElement
from py_core.system.shared import vector_db
from py_core.system.task.parent_guide_recommendation.common import ParentGuideRecommendationAPIResult
from py_core.utils.deepl_translator import DeepLTranslator
from py_core.utils.lookup_translator import LookupTranslator
from py_core.utils.models import DictionaryRow


def convert_messages_to_xml(messages: list[str], params) -> str:
    content = "\n".join([f"  <msg id=\"{i}\">{msg}</msg>" for i, msg in enumerate(messages)])
    return f"""<messages>
{content}
</messages>"""


msg_regex = re.compile(r'<msg id="\d+">(.*?)</msg>')


def convert_xml_to_messages(xml: str, params=None) -> list[str]:
    matches = msg_regex.findall(xml)
    return matches


template = convert_to_jinja_template("""The following XML list contains a list of messages for a parent talking with their child with ASD.
Translate the following messages into Korean.
Note that the messages are intended to be spoken by parent to a kid.
Don't use honorific form of Korean.

{%-if samples is not none and samples | length > 0 %}
<Examples>
Input:
{{stringify(samples | map(attribute='english'), none)}}

Output:
{{stringify(samples | map(attribute='localized'), none)}}
{%-endif-%}
""")


class ParentGuideExampleTranslationParams(ChatCompletionFewShotMapperParams):
    samples: list[DictionaryRow]


def _generate_prompt(input, params: ParentGuideExampleTranslationParams) -> str:
    r = template.render(samples=params.samples, stringify=convert_messages_to_xml)
    print(r)
    return r


class ParentExampleMessageTranslator:

    def __init__(self):
        api = GPTChatCompletionAPI()
        api.config().verbose = False

        self.__dictionary = LookupTranslator("parent_examples",
                                             AACessTalkConfig.parent_example_translation_dictionary_path,
                                             vector_db=vector_db,
                                             verbose=True)

        self.__example_translator: ChatCompletionFewShotMapper[
            list[str], list[str], ParentGuideExampleTranslationParams] = ChatCompletionFewShotMapper(api,
                                                                                                     instruction_generator=_generate_prompt,
                                                                                                     input_str_converter=convert_messages_to_xml,
                                                                                                     output_str_converter=convert_messages_to_xml,
                                                                                                     str_output_converter=convert_xml_to_messages
                                                                                                     )

    async def __translate_examples(self, examples: list[str]) -> list[str]:
        t_start = perf_counter()

        samples = self.__dictionary.query_similar_rows(examples, None, k=5)

        result = await self.__example_translator.run(None, examples, ParentGuideExampleTranslationParams(
            api_params={}, model=ChatGPTModel.GPT_3_5_0613, samples=samples))

        t_end = perf_counter()

        print(f"LLM translation took {t_end - t_start} sec.")

        return result

    async def translate(self, api_result: ParentGuideRecommendationAPIResult) -> ParentGuideRecommendationAPIResult:
        examples = [entry.example for entry in api_result]

        translated_examples = await  self.__translate_examples(examples)
        pass
