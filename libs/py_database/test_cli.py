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
from py_database.database import create_database_engine, get_async_session, create_db_and_tables


GlobalConfig.is_cli_mode = True
GPTChatCompletionAPI.assert_authorize()
DeepLTranslator.assert_authorize()

engine = create_database_engine("database-test.db", verbose=True)
asyncio.run(create_db_and_tables(engine))


dyad_info = asyncio.run(cli_get_dyad_info())
session_info = asyncio.run(cli_get_session_info(dyad_id=dyad_info.id))

print(dyad_info, session_info)

class SessionStorage(SQLSessionStorage):

    @classmethod
    async def _load_session_info(cls, session_id: str) -> SessionInfo | None:
        async with get_async_session(engine) as db:
            print("Find session with id", session_id)
            statement = select(SessionORM).where(SessionORM.id == session_id)
            results = await db.exec(statement)
            session_orm = results.first()
            print("Session orm:", session_orm)
            if session_orm is not None:
                return session_orm.to_data_model()
            else:
                return None




session = asyncio.run(ModeratorSession.create(dyad_info, session_info.topic, session_info.local_timezone, 
                                              SessionStorage(lambda: get_async_session(engine), session_info.id)))

asyncio.run(test_session_loop(session))
