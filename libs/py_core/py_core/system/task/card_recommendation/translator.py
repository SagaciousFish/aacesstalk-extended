from itertools import groupby

import spacy
from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.converter import generate_type_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams
from chatlib.utils.jinja_utils import convert_to_jinja_template

from py_core.config import AACessTalkConfig
from py_core.system.shared import vector_db
from py_core.utils.lookup_translator import LookupTranslator
from py_core.utils.models import DictionaryRow
from .common import ChildCardRecommendationAPIResult


class ChildCardTranslationParams(ChatCompletionFewShotMapperParams):
    similar_cards: list[DictionaryRow] | None


def _stringify_english_word(word: str, category: str) -> str:
    if category == "topic":
        return f"{word} (topic, noun)"
    elif category == "emotion":
        return f"{word} (emotion, adjective/adverb)"
    elif category == "action":
        return f"{word} (action, verb)"


template = convert_to_jinja_template("""
- Given a list of keywords, translate English words into Korean.
- List of cards are provided as a JSON string list with elements formatted as "keyword (category)". Don't translate categories.
- Output should a JSON string list with ONLY keywords.
- Note that the keywords are shown to children with ASD to help with communication.
- Use honorific Korean expressions like "~해요", "~어요" for adjective/adverb/verbs.

{%-if similar_cards is not none and similar_cards | length > 0 %}
<Examples>
{%-for card in similar_cards %}
{{stringify(card.english, card.category)}} => {{card.localized}}
{%-endfor-%}
{%-endif-%}
""")


def _generate_prompt(input, params: ChildCardTranslationParams) -> str:
    return template.render(similar_cards=params.similar_cards, stringify=_stringify_english_word)


str_output_converter, output_str_converter = generate_type_converter(list[str], 'json')


class CardTranslator:

    def __init__(self):
        api = GPTChatCompletionAPI()
        api.config().verbose = False

        self.__nlp = spacy.load("en_core_web_sm")

        self.__mapper = ChatCompletionFewShotMapper[
            list[str], list[str], ChildCardTranslationParams](api,
                                                              _generate_prompt,
                                                              input_str_converter=output_str_converter,
                                                              output_str_converter=output_str_converter,
                                                              str_output_converter=str_output_converter
                                                              )

        self.__dictionary = LookupTranslator("cards", AACessTalkConfig.card_translation_dictionary_path,
                                             vector_db=vector_db,
                                             verbose=True)

    def __transform_original_word(self, word: str) -> str:
        doc = self.__nlp(word)
        return ' '.join([token.text.lower() if token.pos_ != "PROPN" else token.text for token in doc])

    async def translate(self, card_set: ChildCardRecommendationAPIResult) -> list[str]:

        word_list = ([(self.__transform_original_word(word), "topic") for word in card_set.topics] +
                     [(self.__transform_original_word(word), "action") for word in card_set.actions] +
                     [(self.__transform_original_word(word), "emotion") for word in card_set.emotions])

        # Lookup dictionary
        localized_words: list[str | None] = [None] * len(word_list)

        dictionary_hit_count = 0
        for i, (word, category) in enumerate(word_list):
            localized = self.__dictionary.lookup(word, category)
            if localized is not None:
                localized_words[i] = localized
                dictionary_hit_count += 1

        print("Lookup result:", localized_words)

        if len(word_list) - dictionary_hit_count > 0:

            indices_to_translate = [i for i, word in enumerate(localized_words) if word is None]

            words_to_translate = [elm for i, elm in enumerate(word_list)
                                  if localized_words[i] is None]

            similar_card_set: set[DictionaryRow] = set()
            for category, group in groupby(words_to_translate, key=lambda elm: elm[1]):
                l = list(group)
                similar_cards = self.__dictionary.query_similar_rows([word for word, category in l], category, k=5)
                for c in similar_cards:
                    similar_card_set.add(c)

            input = [elm for i, elm in
                     enumerate([_stringify_english_word(word, category) for word, category in word_list])
                     if localized_words[i] is None]

            result = await self.__mapper.run(None, input,
                                             ChildCardTranslationParams(model=ChatGPTModel.GPT_3_5_0125,
                                                                        api_params={},
                                                                        similar_cards=list(similar_card_set)
                                                                        ))
            print(localized_words, result)

            for i, translated in enumerate(result):
                localized_words[indices_to_translate[i]] = translated

                # Update dictionary for future reuse
                word, category = word_list[indices_to_translate[i]]
                self.__dictionary.update(word, category, translated)

            self.__dictionary.write_to_file()

        return localized_words
