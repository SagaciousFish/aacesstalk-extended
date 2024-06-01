from typing import Annotated

from pydantic import BaseModel

from fastapi import APIRouter, Depends
from py_core import ModeratorSession
from py_core.system.model import Dialogue, ParentGuideRecommendationResult, CardIdentity, ChildCardRecommendationResult, \
    CardInfo, ParentExampleMessage

from py_database.model import Dyad

from backend.routers.dyad.common import get_signed_in_dyad, retrieve_moderator_session


router = APIRouter()

class DialogueResponse(BaseModel):
    dyad_id: str
    dialogue: Dialogue

@router.get("/all", response_model=DialogueResponse)
async def get_dialogue(dyad: Annotated[Dyad, Depends(get_signed_in_dyad)], session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]) -> DialogueResponse:
    dialogue = await session.storage.get_dialogue()
    return DialogueResponse(dyad_id=dyad.id, dialogue=dialogue)


class SendParentMessageArgs(BaseModel):
    message: str
    recommendation_id: str

@router.post("/parent/guide", response_model=ParentGuideRecommendationResult)
async def generate_parent_guides(
    session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]):
    guides = await session.generate_parent_guide_recommendation()
    print(guides)
    return guides

@router.post("/parent/message", response_model=ChildCardRecommendationResult)
async def send_parent_message(args: SendParentMessageArgs,
                              session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]):
    return await session.submit_parent_message(parent_message=args.message, recommendation_id=args.recommendation_id)

class RequestExampleArgs(BaseModel):
    recommendation_id: str
    guide_id: str

@router.post("/parent/example", response_model=ParentExampleMessage)
async def request_example_message(
    args: RequestExampleArgs, session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]) -> ParentExampleMessage:
    return await session.request_parent_example_message(**args)


class CardSelectionResult(BaseModel):
    interim_cards: list[CardInfo]
    new_recommendation: ChildCardRecommendationResult


@router.post("/child/add_card", response_model=CardSelectionResult)
async def select_card(card_identity: CardIdentity,
                      session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]):
    interim_selection = await session.select_child_card(card_identity)
    interim_cards = await session.get_card_info_from_identities(interim_selection.cards)
    new_recommendation = await session.refresh_child_card_recommendation()
    return CardSelectionResult(interim_cards=interim_cards, new_recommendation=new_recommendation)


@router.put("/child/refresh_cards", response_model=ChildCardRecommendationResult)
async def refresh_card_selection(
        session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]) -> ChildCardRecommendationResult:
    return await session.refresh_child_card_recommendation()


@router.post("/child/confirm_cards", response_model=ParentGuideRecommendationResult)
async def confirm_child_card_selection(
        session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]) -> ParentGuideRecommendationResult:
    return await session.confirm_child_card_selection()
