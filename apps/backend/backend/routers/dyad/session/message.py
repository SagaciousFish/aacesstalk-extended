from functools import cache
from typing import Annotated

from pydantic import BaseModel

from fastapi import APIRouter, Depends

from backend.database import get_db_session
from py_core import ModeratorSession
from py_core.system.model import Dialogue, ParentGuideRecommendationResult, CardIdentity, ChildCardRecommendationResult
from py_database import SQLSessionStorage

from py_database.database import AsyncSession

router = APIRouter()

sessions: dict[str, ModeratorSession] = {}


def get_moderator_session(session_id: str, db: AsyncSession) -> ModeratorSession:
    if session_id in sessions:
        session = sessions[session_id]
        session.storage = db
        return session
    else:
        session = ModeratorSession(SQLSessionStorage(db, session_id))
        sessions[session_id] = session
        return session


def depends_on_moderator_session(session_id: str, db: Annotated[AsyncSession, Depends(get_db_session)]):
    return Depends(lambda: get_moderator_session(session_id, db))


@router.get("/all", response_class=Dialogue)
async def get_dialogue(session: Annotated[ModeratorSession, depends_on_moderator_session]) -> Dialogue:
    return await session.storage.get_dialogue()


class SendParentMessageArgs(BaseModel):
    message: str
    recommendation_id: str


@router.post("/add/parent", response_model=ChildCardRecommendationResult)
async def send_parent_message(args: SendParentMessageArgs, session: Annotated[ModeratorSession, depends_on_moderator_session]):
    return await session.submit_parent_message(parent_message=args.message, recommendation_id=args.recommendation_id)


class SendChildCardSelectionArgs(BaseModel):
    selected_cards: list[CardIdentity]


@router.post("/add/child")
async def send_child_card_selection(session_id: str,
                                    args: SendChildCardSelectionArgs,
                                    session: Annotated[ModeratorSession, depends_on_moderator_session]):
    pass
