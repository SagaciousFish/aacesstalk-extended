from pydantic import BaseModel

from fastapi import APIRouter, Depends

from backend.database import get_db_session
from py_core.system.model import Dialogue, ParentGuideRecommendationResult, CardIdentity

from py_database.database import AsyncSession

router = APIRouter()

@router.get("/messages/all")
async def get_dialogue(session_id: str,
                       session: AsyncSession = Depends(get_db_session)) -> Dialogue:
    pass


class SendParentMessageArgs(BaseModel):
    parent_message: str
    current_parent_guide: ParentGuideRecommendationResult | None = None


@router.post("/messages/add/parent")
async def send_parent_message(session_id: str,
                              args: SendParentMessageArgs,
                              session: AsyncSession = Depends(get_db_session)):
    pass


class SendChildCardSelectionArgs(BaseModel):
    selected_cards: list[CardIdentity]


@router.post("/messages/add/child")
async def send_child_card_selection(session_id: str,
                                    args: SendChildCardSelectionArgs,
                                    session: AsyncSession = Depends(get_db_session)):
    pass
