from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, desc
from backend.database import AsyncSession
from py_core.system.model import SessionInfo, Dialogue, DialogueRole, DialogueMessage, ParentGuideElement, ParentGuideCategory, DialogueInspectionCategory, ParentGuideType
from py_database.model import SessionORM, DialogueMessageORM, SessionStatus, ParentGuideRecommendationResultORM, ParentExampleMessageORM, InteractionORM, InteractionType
from sqlmodel import select, col

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


class ParentGuideInfo(BaseModel):
    id: str
    category: ParentGuideCategory | list[DialogueInspectionCategory]
    type: ParentGuideType = ParentGuideType.Messaging
    guide: str
    guide_localized: str | None = None
    example: str | None = None
    example_localized: str | None = None
    example_accessed: bool = False


class ExtendedMessage(DialogueMessage):
    model_config = ConfigDict(frozen=False)
    guides: Optional[list[ParentGuideInfo]] = None

class DialogueSession(BaseModel):
    id: str
    dialogue: list[ExtendedMessage]



async def get_dialogue(session_id: str, db: AsyncSession) -> DialogueSession:
    messages_result = await db.exec((select(DialogueMessageORM).where(DialogueMessageORM.session_id == session_id)
        .order_by(DialogueMessageORM.timestamp)))
    messages : list[DialogueMessageORM] = [row.to_data_model() for row in messages_result.all()]

    parent_guide_results = await db.exec((select(ParentGuideRecommendationResultORM)
                          .where(ParentGuideRecommendationResultORM.session_id == session_id)))

    guide_sets = [row.to_data_model() for row in parent_guide_results.all()]

    example_message_results = await db.exec((select(ParentExampleMessageORM).where(ParentExampleMessageORM.session_id == session_id)))
    example_messages = [row.to_data_model() for row in example_message_results]

    example_log_results = await db.exec((select(InteractionORM)
                         .where(InteractionORM.type == InteractionType.RequestParentExampleMessage)
                         .where(col(InteractionORM.turn_id).in_({msg.turn_id for msg in messages}))))
    example_access_logs: list[InteractionORM] = example_log_results.all()

    extended_messages = [ExtendedMessage(**message.model_dump()) for message in messages]
    for msg in extended_messages:
        if msg.role == DialogueRole.Parent:
            recommendation = next((row for row in guide_sets if row.turn_id == msg.turn_id), None)
            if recommendation is not None:
                guides = [ParentGuideInfo(**guide.model_dump(include={"id", "category", "type", "guide", "guide_localized"})) for guide in recommendation.guides]
                for guide in guides:
                    if guide.type == ParentGuideType.Messaging:
                        example_message = next((row for row in example_messages if row.guide_id == guide.id), None)
                        if example_message is not None:
                            guide.example = example_message.message
                            guide.example_localized = example_message.message_localized
                            access_log = next((row for row in example_access_logs if row.turn_id == msg.turn_id and row.metadata_json["example_message_id"] == example_message.id), None)
                            guide.example_accessed = access_log is not None
                
                msg.guides = guides


    return DialogueSession(id=session_id, 
                           dialogue=extended_messages)

