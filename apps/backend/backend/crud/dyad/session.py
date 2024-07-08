from pydantic import BaseModel
from sqlalchemy import func, desc
from backend.database import AsyncSession
from py_core.system.model import SessionInfo, Dialogue
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


async def get_session_summaries(dyad_id: str, db: AsyncSession, includeOnlyTerminated: bool = True) -> list[ExtendedSessionInfo]:
    statement = (select(SessionORM, func.count(DialogueMessageORM.session_id).label('num_turns'))
        .join(DialogueMessageORM, SessionORM.id == DialogueMessageORM.session_id, isouter=False if includeOnlyTerminated else True)
        .where(SessionORM.dyad_id == dyad_id))

    if includeOnlyTerminated is True:
        statement = statement.where(SessionORM.status == SessionStatus.Terminated)
     
    statement = statement.group_by(SessionORM.id).order_by(desc(SessionORM.started_timestamp))
    
    result = await db.exec(statement)

    return [ExtendedSessionInfo(**row[0].to_data_model().model_dump(), num_turns=row[1]) for row in result.all()]

class DialogueSession(BaseModel):
    id: str
    dialogue: Dialogue

async def get_dialogue(session_id: str, db: AsyncSession) -> Dialogue:
    statement = (select(DialogueMessageORM).where(DialogueMessageORM.session_id == session_id)
        .order_by(DialogueMessageORM.timestamp))
    
    result = await db.exec(statement)

    return DialogueSession(id=session_id, dialogue=[row.to_data_model() for row in result.all()])

