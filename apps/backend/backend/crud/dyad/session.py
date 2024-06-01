from backend.database import AsyncSession
from py_database.model import Session as SessionORM, Dyad
from chatlib.utils.time import get_timestamp
from sqlmodel import select
from py_core.system.model import Session
from py_core.system.session_topic import SessionTopicInfo

from backend.routers.dyad.session.moderator import get_moderator_session


async def create_moderator_session(dyad: Dyad, topic: SessionTopicInfo, timezone: str, db: AsyncSession) -> SessionORM:
    s = SessionORM.from_data_model(Session(topic=topic, local_timezone=timezone), dyad_id=dyad.id)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s

async def find_session_orm(session_id: str, dyad_id: str, db: AsyncSession)-> SessionORM | None:
    statement = (select(SessionORM)
                 .where(SessionORM.id == session_id)
                 .where(SessionORM.dyad_id == dyad_id)
                 .limit(1))
    results = await db.exec(statement)
    return results.first()

async def end_session(session_id: str, dyad_id: str, db: AsyncSession):
   s = await find_session_orm(session_id, dyad_id, db)
   if s is not None:
       s.ended_timestamp = get_timestamp()
       db.add(s)
       await db.commit()
   else:
       ValueError("No such session with the id and dyad id.")


async def abort_session(session_id: str, dyad_id: str, db: AsyncSession):
   s = await find_session_orm(session_id, dyad_id, db)
   if s is not None:
       await get_moderator_session(session_id, db).storage.delete_entities()
       await db.delete(s)
   else:
       ValueError("No such session with the id and dyad id.")
