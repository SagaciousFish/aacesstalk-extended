from typing import Annotated
from fastapi import Depends
from py_database import SQLSessionStorage

from py_database.database import AsyncSession

from backend.database import get_db_session
from py_core.system.moderator import ModeratorSession

sessions: dict[str, ModeratorSession] = {}


def get_moderator_session(session_id: str, db: AsyncSession) -> ModeratorSession:
    if session_id in sessions:
        session = sessions[session_id]
        if isinstance(session.storage, SQLSessionStorage):
            session.storage.sql_session = db
        return session
    else:
        session = ModeratorSession(SQLSessionStorage(db, session_id))
        sessions[session_id] = session
        return session


def retrieve_moderator_session(session_id: str, db: Annotated[AsyncSession, Depends(get_db_session)]):
    return get_moderator_session(session_id, db)