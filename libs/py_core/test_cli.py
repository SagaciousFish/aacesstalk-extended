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

session_info = asyncio.run(cli_get_session_info(dyad_info.id))

print(dyad_info, session_info)

moderator_session = asyncio.run(ModeratorSession.create(dyad_info, session_info.topic, session_info.local_timezone, JsonSessionStorage(session_info.id)))

asyncio.run(test_session_loop(moderator_session))
