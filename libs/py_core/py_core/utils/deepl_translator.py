from asyncio import to_thread
from time import perf_counter
from typing import Any, Union, Iterable

import deepl
from chatlib.utils.integration import IntegrationService, APIAuthorizationVariableSpec,  APIAuthorizationVariableSpecPresets, APIAuthorizationVariableType
from deepl import TextResult, SplitSentences


class DeepLTranslator(IntegrationService):
    __api_key_spec = APIAuthorizationVariableSpecPresets.ApiKey

    @classmethod
    def provider_name(cls) -> str:
        return "Deepl"

    @classmethod
    def get_auth_variable_specs(cls) -> list[APIAuthorizationVariableSpec]:
        return [cls.__api_key_spec]

    @classmethod
    def _authorize_impl(cls, variables: dict[APIAuthorizationVariableSpec, Any]) -> bool:
        if variables[cls.__api_key_spec] is not None:
            return True
        else:
            return False

    def __init__(self):
        self.__client = deepl.Translator(self.get_auth_variable_for_spec(self.__api_key_spec))

    async def translate(self, text: Union[str, Iterable[str]], source_lang: str, target_lang: str,
                        context: str | None = None,
                        split_sentences: str | SplitSentences | None = SplitSentences.OFF
                        ) -> Union[str, list[str]]:
        t_start = perf_counter()
        result: Union[TextResult, list[TextResult]] = await to_thread(self.__client.translate_text,
                                                                      text=text,
                                                                      source_lang=source_lang,
                                                                      target_lang=target_lang,
                                                                      context=context,
                                                                      split_sentences=split_sentences,
                                                                      )
        t_end = perf_counter()

        print(f"DeepL translation took {t_end - t_start} sec.")

        if isinstance(result, TextResult):
            return result.text
        else:
            return [r.text for r in result]
