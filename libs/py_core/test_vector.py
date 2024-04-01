import asyncio

from chatlib.global_config import GlobalConfig
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI
from py_core import ModeratorSession
from py_core.cli import test_session_loop
from py_core.config import AACessTalkConfig
from py_core.system.storage.json import SessionJsonStorage
from py_core.system.task.card_recommendation.translator import CardTranslator
from py_core.utils.deepl_translator import DeepLTranslator
from py_core.utils.lookup_translator import LookupTranslator

GlobalConfig.is_cli_mode = True
GPTChatCompletionAPI.assert_authorize()
DeepLTranslator.assert_authorize()

card_translator = LookupTranslator("cards", AACessTalkConfig.card_translation_dictionary_path, verbose=True)

print(card_translator.vector_db.collection_cards.count())

cards = card_translator.query_similar_rows("cards", ["Climb"], "action", 4)
print(cards)
