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


async def end_session(session_id: str, dyad_id: str, db: AsyncSession):
    statement = (select(Session)
                 .where(Session.id == session_id)
                 .where(Session.dyad.id == dyad_id)
                 .limit(1))
    results = await db.exec(statement)
    s = results.first()
    if s is not None:
        s.ended_timestamp = get_timestamp()
        await db.commit()
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")
