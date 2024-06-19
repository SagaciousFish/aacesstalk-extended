import asyncio

from chatlib.global_config import GlobalConfig
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI
from py_core import ModeratorSession
from py_core.cli import test_session_loop, cli_get_session_info, cli_get_dyad_info
from py_core.system.model import SessionInfo
from py_core.utils.deepl_translator import DeepLTranslator
from sqlmodel import select
from py_database import SQLSessionStorage
from py_database.model import SessionORM
from py_database.database import create_database_engine, make_async_session_maker, create_db_and_tables


GlobalConfig.is_cli_mode = True
GPTChatCompletionAPI.assert_authorize()
DeepLTranslator.assert_authorize()

engine = create_database_engine("database-test.db", verbose=True)
asyncio.run(create_db_and_tables(engine))


dyad_info = asyncio.run(cli_get_dyad_info())
session_info = asyncio.run(cli_get_session_info(dyad_id=dyad_info.id))

print(dyad_info, session_info)

SQLSessionStorage.set_session_maker(make_async_session_maker(engine))

session = asyncio.run(ModeratorSession.create(dyad_info, session_info.topic, session_info.local_timezone, 
                                              SQLSessionStorage(session_info.id)))

asyncio.run(test_session_loop(session))
