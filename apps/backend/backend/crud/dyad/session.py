from backend.database import AsyncSession
from py_database.model import SessionORM, DyadORM
from chatlib.utils.time import get_timestamp
from sqlmodel import select
from py_core.system.model import SessionInfo
from py_core.system.session_topic import SessionTopicInfo
from py_database.storage import SQLSessionStorage


async def create_moderator_session(dyad: DyadORM, topic: SessionTopicInfo, timezone: str, db: AsyncSession) -> SessionORM:
    s = SessionORM.from_data_model(SessionInfo(topic=topic, local_timezone=timezone), dyad_id=dyad.id)
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
