import asyncio
import re
from os import path, getcwd
from random import shuffle
from time import perf_counter

import yaml

from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams, \
    MapperInputOutputPair
from chatlib.utils.env_helper import get_env_variable
from pydantic import BaseModel, TypeAdapter

from py_core.system.model import ParentGuideElement
from py_core.system.task.parent_guide_recommendation.common import ParentGuideRecommendationAPIResult
from py_core.utils.deepl_translator import DeepLTranslator


class ExampleTranslationSample(BaseModel):
    en: str
    kr: str


def convert_sample_to_pair(samples: list[ExampleTranslationSample]) -> MapperInputOutputPair[list[str], list[str]]:
    return MapperInputOutputPair(
        input=[s.en for s in samples],
        output=[s.kr for s in samples]
    )


example_translation_sample_list_type_adapter = TypeAdapter(list[list[ExampleTranslationSample]])


class ExampleTranslationSampleFactory:

    def __init__(self, filepath: str):
        self.__samples: list[list[ExampleTranslationSample]] = []

        with open(filepath, 'r') as file:
            self.__samples = example_translation_sample_list_type_adapter.validate_python(yaml.safe_load(file))

    async def retrieve_samples(self, input_list: list[str], n: int = 5) -> list[
        MapperInputOutputPair[list[str], list[str]]]:
        copied = [s for s in self.__samples]
        shuffle(copied)
        return [convert_sample_to_pair(s) for s in copied[:min(len(copied), n)]]


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

        self.__example_translation_sample_factory = ExampleTranslationSampleFactory(
            path.join(getcwd(), "../../data/parent_example_translation_samples.yml"))

        # Initialize DeepL
        self.__deepl_translator = DeepLTranslator()

    async def __translate_examples(self, examples: list[str]) -> list[str]:
        t_start = perf_counter()

        samples = await self.__example_translation_sample_factory.retrieve_samples(examples, n=3)

        result = await self.__example_translator.run(samples, examples, self.__TRANSLATOR_PARAMS__)

        t_end = perf_counter()

        print(f"LLM translation took {t_end - t_start} sec.")

        return result

    async def translate(self, api_result: ParentGuideRecommendationAPIResult) -> ParentGuideRecommendationAPIResult:
        examples = [entry.example for entry in api_result]
        guides = [entry.guide for entry in api_result]

        coroutine_translate_examples = self.__translate_examples(examples)

        coroutine_translate_guides = self.__deepl_translator.translate(
            text=guides,
            source_lang="EN",
            target_lang="KO",
            context="The phrases are guides for parents' communication with children with Autism Spectrum Disorder."
        )

        translated_examples, translated_guides = await asyncio.gather(coroutine_translate_examples,
                                                                      coroutine_translate_guides)

        return [ParentGuideElement(example=example, guide=guide) for example, guide in
                zip(translated_examples, translated_guides)]
