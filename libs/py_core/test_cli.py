import asyncio

from chatlib.global_config import GlobalConfig
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI
from py_core import ModeratorSession
from py_core.cli import cli_get_session_info, test_session_loop, cli_get_dyad_info
from py_core.system.storage.session.json import JsonSessionStorage
from py_core.utils.deepl_translator import DeepLTranslator

GlobalConfig.is_cli_mode = True
GPTChatCompletionAPI.assert_authorize()
DeepLTranslator.assert_authorize()

dyad_info = asyncio.run(cli_get_dyad_info())

session_info = asyncio.run(cli_get_session_info())

print(dyad_info, session_info)

session = ModeratorSession(dyad_info, JsonSessionStorage(session_info))

asyncio.run(test_session_loop(session))
