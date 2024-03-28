from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.converter import generate_type_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams

from py_core.config import AACessTalkConfig
from py_core.utils.lookup_translator import LookupTranslator
from .common import ChildCardRecommendationAPIResult
import spacy


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

        self.__nlp = spacy.load("en_core_web_sm")

        self.__mapper = ChatCompletionFewShotMapper[
            list[str], list[str], ChildCardTranslationParams](api,
                                                              _prompt,
                                                              input_str_converter=output_str_converter,
                                                              output_str_converter=output_str_converter,
                                                              str_output_converter=str_output_converter
                                                              )

        self.__dictionary = LookupTranslator(AACessTalkConfig.card_translation_dictionary_path, verbose=True)
        self.__dictionary.load_file()

    def __transform_original_word(self, word: str) -> str:
        doc = self.__nlp(word)
        return ' '.join([token.text.lower() if token.pos_ != "PROPN" else token.text for token in doc])

    async def translate(self, card_set: ChildCardRecommendationAPIResult) -> list[str]:
        word_list = ([(self.__transform_original_word(word), "topic") for word in card_set.topics] +
                     [(self.__transform_original_word(word), "action") for word in card_set.actions] +
                     [(self.__transform_original_word(word), "emotion") for word in card_set.emotions])

        # Lookup dictionary
        localized_words: list[str|None] = [None] * len(word_list)

        dictionary_hit_count = 0
        for i, (word, category) in enumerate(word_list):
            localized = self.__dictionary.lookup(word, category)
            if localized is not None:
                localized_words[i] = localized
                dictionary_hit_count += 1

        print("Lookup result:", localized_words)

        if len(word_list) - dictionary_hit_count > 0:
            indices_to_translate = [i for i, word in enumerate(localized_words) if word is None]

            card_set_list = [elm for i, elm in enumerate([f"{word} (topic, noun)" for word in card_set.topics] + [f"{word} (action, verb)" for
                                                                                     word
                                                                                     in card_set.actions] + [
                                f"{word} (emotion, adjective/adverb)" for word in
                                card_set.emotions]) if localized_words[i] is None]


            result = await self.__mapper.run(None, card_set_list,
                                             ChildCardTranslationParams(model=ChatGPTModel.GPT_3_5_0125,
                                                                        api_params={}))
            print(localized_words, result)

            for i, translated in enumerate(result):
                localized_words[indices_to_translate[i]] = translated

                # Update dictionary for future reuse
                word, category = word_list[indices_to_translate[i]]
                self.__dictionary.update(word, category, translated)

            self.__dictionary.write_to_file()

        return localized_words
