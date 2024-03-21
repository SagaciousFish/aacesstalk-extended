from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.converter import generate_type_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams

from .common import ChildCardRecommendationAPIResult


class ChildCardTranslationParams(ChatCompletionFewShotMapperParams):
    pass


_prompt = """
- Given a list of keywords, translate English words into Korean.
- List of cards are provided as a JSON string list with elements formatted as "keyword (category)". Don't translate categories.
- Output should a JSON string list with ONLY keywords.
- Note that the keywords are shown to children with ASD to help with communication.
- Use honorific Korean expressions like "~해요", "~어요" for adjective/adverb/verbs.
"""

str_output_converter, output_str_converter = generate_type_converter(list[str], 'json')


class CardTranslator:

    def __init__(self):
        api = GPTChatCompletionAPI()
        api.config().verbose = False

        self.__mapper = ChatCompletionFewShotMapper[
            list[str], list[str], ChildCardTranslationParams](api,
                                                              _prompt,
                                                              input_str_converter=output_str_converter,
                                                              output_str_converter=output_str_converter,
                                                              str_output_converter=str_output_converter
                                                              )

    async def translate(self, card_set: ChildCardRecommendationAPIResult) -> list[str]:
        card_set_list = [f"{word} (topic, noun)" for word in card_set.topics] + [f"{word} (action, verb)" for
                                                                                 word
                                                                                 in card_set.actions] + [
                            f"{word} (emotion, adjective/adverb)" for word in
                            card_set.emotions]
        result = await self.__mapper.run(None, card_set_list,
                                         ChildCardTranslationParams(model=ChatGPTModel.GPT_3_5_0125,
                                                                    api_params={}))
        return result
