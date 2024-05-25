from chatlib.global_config import GlobalConfig
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI
from py_core.config import AACessTalkConfig
from py_core.utils.deepl_translator import DeepLTranslator
from py_core.utils.lookup_translator import LookupTranslator

GlobalConfig.is_cli_mode = True
GPTChatCompletionAPI.assert_authorize()
DeepLTranslator.assert_authorize()

card_translator = LookupTranslator("cards", AACessTalkConfig.card_translation_dictionary_path, verbose=True)

print(card_translator.vector_db.get_collection("cards").count())

cards = card_translator.query_similar_rows(["Climb"], "action", 4)
print(cards)
