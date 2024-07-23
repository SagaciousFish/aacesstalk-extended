from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, desc
from backend.database import AsyncSession
from py_core.system.model import CardInfo, CardCategory, SessionInfo, Dialogue, DialogueRole, DialogueMessage, ParentGuideElement, ParentGuideCategory, DialogueInspectionCategory, ParentGuideType
from py_database.model import SessionORM, DialogueMessageORM, DialogueTurnORM, SessionStatus, ParentGuideRecommendationResultORM, ParentExampleMessageORM, InteractionORM, InteractionType
from sqlmodel import select, col
import pandas as pd
from pandas import DataFrame
from math import floor
import pendulum

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
    duration_sec: float

class DialogueSession(BaseModel):
    id: str
    dialogue: list[ExtendedMessage]


async def get_dialogue(session_id: str, db: AsyncSession) -> DialogueSession:
    messages_result = await db.exec((select(DialogueMessageORM, DialogueTurnORM).where(DialogueMessageORM.turn_id == DialogueTurnORM.id).where(DialogueMessageORM.session_id == session_id)
        .order_by(DialogueMessageORM.timestamp)))
    messages : list[tuple[DialogueMessage, DialogueTurnORM]] = [(msg.to_data_model(), turn) for msg, turn in messages_result.all()]

    parent_guide_results = await db.exec((select(ParentGuideRecommendationResultORM)
                          .where(ParentGuideRecommendationResultORM.session_id == session_id)))

    guide_sets = [row.to_data_model() for row in parent_guide_results.all()]

    example_message_results = await db.exec((select(ParentExampleMessageORM).where(ParentExampleMessageORM.session_id == session_id)))
    example_messages = [row.to_data_model() for row in example_message_results]

    example_log_results = await db.exec((select(InteractionORM)
                         .where(InteractionORM.type == InteractionType.RequestParentExampleMessage)
                         .where(col(InteractionORM.turn_id).in_({msg.turn_id for msg, turn in messages}))))
    example_access_logs: list[InteractionORM] = example_log_results.all()

    extended_messages = [ExtendedMessage(**message.model_dump(), duration_sec=((turn.ended_timestamp - turn.started_timestamp)/1000)) for message, turn in messages]
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

_CARD_CATEGORIES = [CardCategory.Topic, CardCategory.Emotion, CardCategory.Action, CardCategory.Core]

async def make_user_dataset_table(dyad_id: str, db: AsyncSession) -> tuple[DataFrame, DataFrame]:
    terminated_sessions: list[SessionORM] = (await db.exec(select(SessionORM).where(SessionORM.dyad_id == dyad_id)
                                         .where(SessionORM.status == SessionStatus.Terminated))).all()
    
    cleaned_sessions: list[dict] = []
    cleaned_turns: list[dict] = []
    
    for session in terminated_sessions:
        dialogue_session = await get_dialogue(session.id, db)

        time = pendulum.from_timestamp(session.started_timestamp/1000, session.local_timezone)
        session_date_string = time.format("YYYY-MM-DD")
        session_time_string = time.format("HH:mm:ss")
        

        # Make session rows
        parent_messages = [msg for msg in dialogue_session.dialogue if msg.role == DialogueRole.Parent]
        child_messages = [msg for msg in dialogue_session.dialogue if msg.role == DialogueRole.Child]
        
        session_row = dict(
            id=session.id,
            date=session_date_string,
            time_of_day=session_time_string,
            duration_sec=(session.ended_timestamp - session.started_timestamp)/1000,
            num_parent_msgs=len(parent_messages),
            num_child_msgs=len(child_messages),
        )
        cleaned_sessions.append(session_row)
        
        # Make dialogue rows
        for message_i, message in enumerate(dialogue_session.dialogue):
            if message.role == DialogueRole.Parent:

                child_message_exists = message_i < len(dialogue_session.dialogue)-1 and dialogue_session.dialogue[message_i+1].role == DialogueRole.Child

                row = dict(
                    dialogue_id = session.id,
                    dialogue_timestamp = session.started_timestamp,
                    dialogue_date = session_date_string,
                    order = floor(message_i/2),
                    parent_duration_sec = message.duration_sec,
                    child_duration_sec = dialogue_session.dialogue[message_i+1].duration_sec if child_message_exists else None,
                    message = message.content_localized or message.content
                )

                messaging_guides = [gd for gd in message.guides if gd.type == ParentGuideType.Messaging]
                guides_output = {str(g_i+1):gd.model_dump(include={"category", "guide_localized", "example_localized", "example_accessed"}) for g_i, gd in enumerate(messaging_guides)}
                print(guides_output)

                feedback = next((gd for gd in message.guides if gd.type == ParentGuideType.Feedback), None)
                if feedback is not None:
                    guides_output["feedback"] = dict(
                        category=", ".join(feedback.category),
                        guide_localized = feedback.guide_localized
                    )
                row["parent_guides"] = guides_output

                if child_message_exists:
                    cards: list[CardInfo] = dialogue_session.dialogue[message_i+1].content
                    row["child_cards"] = ", ".join([f"[{card.label_localized}]" for card in cards])
                    row["child_cards_by_type"] = {category:", ".join([f"[{c.label_localized}]" for c in cards if c.category == category]) for category in _CARD_CATEGORIES}
                    row["child_cards_count_by_type"] = {category:len([c.label_localized for c in cards if c.category == category]) for category in _CARD_CATEGORIES}
                
                cleaned_turns.append(row)
    
    turn_table = pd.json_normalize(cleaned_turns)
    session_table = pd.json_normalize(cleaned_sessions)

    return session_table, turn_table