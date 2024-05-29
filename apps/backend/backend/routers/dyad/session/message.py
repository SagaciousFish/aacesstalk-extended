from functools import cache
from typing import Annotated

from pydantic import BaseModel

from fastapi import APIRouter, Depends

from backend.database import get_db_session
from py_core import ModeratorSession
from py_core.system.model import Dialogue, ParentGuideRecommendationResult, CardIdentity, ChildCardRecommendationResult, \
    CardInfo, ParentExampleMessage

from backend.moderator import depends_on_moderator_session


router = APIRouter()



@router.get("/all", response_model=Dialogue)
async def get_dialogue(session: Annotated[ModeratorSession, depends_on_moderator_session]) -> Dialogue:
    return await session.storage.get_dialogue()


class SendParentMessageArgs(BaseModel):
    message: str
    recommendation_id: str


@router.post("/parent/message", response_model=ChildCardRecommendationResult)
async def send_parent_message(args: SendParentMessageArgs,
                              session: Annotated[ModeratorSession, depends_on_moderator_session]):
    return await session.submit_parent_message(parent_message=args.message, recommendation_id=args.recommendation_id)


@router.post("/parent/example", response_model=ParentExampleMessage)
async def request_example_message(
        session: Annotated[ModeratorSession, depends_on_moderator_session]) -> ParentExampleMessage:
    return await session.request_parent_example_message()


class CardSelectionResult(BaseModel):
    interim_cards: list[CardInfo]
    new_recommendation: ChildCardRecommendationResult


@router.post("/card_selection/add", response_model=CardSelectionResult)
async def select_card(card_identity: CardIdentity,
                      session: Annotated[ModeratorSession, depends_on_moderator_session]):
    interim_selection = await session.select_child_card(card_identity)
    interim_cards = await session.get_card_info_from_identities(interim_selection.cards)
    new_recommendation = await session.refresh_child_card_recommendation()
    return CardSelectionResult(interim_cards=interim_cards, new_recommendation=new_recommendation)


@router.put("/card_selection/refresh", response_model=ChildCardRecommendationResult)
async def refresh_card_selection(
        session: Annotated[ModeratorSession, depends_on_moderator_session]) -> ChildCardRecommendationResult:
    return await session.refresh_child_card_recommendation()


@router.post("/card_selection/confirm", response_model=ParentGuideRecommendationResult)
async def confirm_child_card_selection(
        session: Annotated[ModeratorSession, depends_on_moderator_session]) -> ParentGuideRecommendationResult:
    return await session.confirm_child_card_selection()
