from backend.database import AsyncSession
from py_database.model import Session, Dyad
from chatlib.utils.time import get_timestamp
from sqlmodel import select
from fastapi import HTTPException, status


async def create_moderator_session(dyad: Dyad, timezone: str, db: AsyncSession) -> Session:
    s = Session(dyad_id=dyad.id, local_timezone=timezone)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s

async def find_session(session_id: str, dyad_id: str, db: AsyncSession)-> Session | None:
    statement = (select(Session)
                 .where(Session.id == session_id)
                 .where(Session.dyad.id == dyad_id)
                 .limit(1))
    results = await db.exec(statement)
    return results.first()

async def end_session(session_id: str, dyad_id: str, db: AsyncSession):
   s = await find_session(session_id, dyad_id, db)
   if s is not None:
       s.ended_timestamp = get_timestamp()
       db.add(s)
       await db.commit()
   else:
       ValueError("No such session with the id and dyad id.")
