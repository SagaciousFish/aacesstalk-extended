import asyncio

from chatlib.global_config import GlobalConfig
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI
from py_core import ModeratorSession
from py_core.cli import test_session_loop
from py_database import SQLSessionStorage
from py_database.database import create_database_engine, get_async_session


GlobalConfig.is_cli_mode = True
GPTChatCompletionAPI.assert_authorize()

engine = create_database_engine("database.db", verbose=True)
session = get_async_session(engine)

session = ModeratorSession(SQLSessionStorage(session))

asyncio.run(test_session_loop(session))
