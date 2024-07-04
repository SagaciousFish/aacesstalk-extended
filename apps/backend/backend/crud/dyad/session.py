from pydantic import BaseModel
from sqlalchemy import func
from backend.database import AsyncSession
from py_core.system.model import SessionInfo
from py_database.model import SessionORM, DialogueMessageORM, SessionStatus
from sqlmodel import select

async def find_session_orm(session_id: str, dyad_id: str, db: AsyncSession)-> SessionORM | None:
    statement = (select(SessionORM)
                 .where(SessionORM.id == session_id)
                 .where(SessionORM.dyad_id == dyad_id)
                 .limit(1))
    results = await db.exec(statement)
    return results.first()

class ExtendedSessionInfo(SessionInfo):
    num_turns: int


async def get_session_summaries(dyad_id: str, db: AsyncSession) -> list[ExtendedSessionInfo]:
    statement = (select(SessionORM, func.count(DialogueMessageORM.session_id).label('num_turns'))
        .join(DialogueMessageORM, SessionORM.id == DialogueMessageORM.session_id)
        .where(SessionORM.dyad_id == dyad_id)
        .where(SessionORM.status == SessionStatus.Terminated)
        .group_by(SessionORM.id)
        )
    
    result = await db.exec(statement)

    return [ExtendedSessionInfo(**row[0].to_data_model().model_dump(), num_turns=row[1]) for row in result.all()]