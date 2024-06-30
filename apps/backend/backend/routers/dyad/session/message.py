from typing import Annotated

from pydantic import BaseModel

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from py_core import ModeratorSession
from py_core.system.model import Dialogue, DialogueTurn, ParentGuideRecommendationResult, CardIdentity, ChildCardRecommendationResult, \
    CardInfo, ParentExampleMessage, InterimCardSelection

from py_core.utils.speech import ClovaSpeech

from py_database.model import DyadORM

from backend.routers.dyad.common import get_signed_in_dyad_orm, retrieve_moderator_session

from typing import TypeVar, Generic

from backend.routers.errors import ErrorType
T = TypeVar('T')

class ResponseWithTurnId(BaseModel, Generic[T]):
    payload: T
    next_turn_id: str

router = APIRouter()


asr_engine = ClovaSpeech()

class DialogueResponse(BaseModel):
    dyad_id: str
    dialogue: Dialogue

@router.get("/all", response_model=DialogueResponse)
async def get_dialogue(dyad: Annotated[DyadORM, Depends(get_signed_in_dyad_orm)], session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]) -> DialogueResponse:
    dialogue = await session.storage.get_dialogue()
    return DialogueResponse(dyad_id=dyad.id, dialogue=dialogue)


class SendParentMessageArgs(BaseModel):
    message: str

@router.post("/parent/message/text", response_model=ResponseWithTurnId[ChildCardRecommendationResult])
async def send_parent_message_text(args: SendParentMessageArgs,
                              session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]) -> ResponseWithTurnId[ChildCardRecommendationResult]:
    turn, recommendation = await session.submit_parent_message(parent_message=args.message)
    return ResponseWithTurnId(payload=recommendation, next_turn_id=turn.id)



@router.post('/parent/message/audio')
async def send_parent_message_audio(file: Annotated[UploadFile, File()], turn_id: Annotated[str, Form()], session_id: str, session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]) -> ResponseWithTurnId[ChildCardRecommendationResult]:
    try:
        print("Dictate parent turn audio...")
        text = await asr_engine.recognize_speech(file.filename, file.file, file.content_type)
        if len(text) > 0:
            turn, recommendation = await session.submit_parent_message(parent_message=text)
            return ResponseWithTurnId(payload=recommendation, next_turn_id=turn.id)
        else:
            raise HTTPException(status_code=500, detail=ErrorType.EmptyDictation)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex.__str__) from ex

class RequestExampleArgs(BaseModel):
    recommendation_id: str
    guide_id: str

@router.post("/parent/example", response_model=ParentExampleMessage)
async def request_example_message(
    args: RequestExampleArgs, session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]) -> ParentExampleMessage:
    return await session.request_parent_example_message(**args.model_dump())


class CardSelectionResult(BaseModel):
    interim_cards: list[CardInfo]
    new_recommendation: ChildCardRecommendationResult


@router.post("/child/add_card", response_model=CardSelectionResult)
async def append_card(card_identity: CardIdentity,
                      session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]):
    interim_selection = await session.append_child_card(card_identity)
    interim_cards = await session.get_card_info_from_identities(interim_selection.cards)
    new_recommendation = await session.refresh_child_card_recommendation()
    return CardSelectionResult(interim_cards=interim_cards, new_recommendation=new_recommendation)


@router.put("/child/refresh_cards", response_model=ChildCardRecommendationResult)
async def refresh_card_selection(
        session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]) -> ChildCardRecommendationResult:
    return await session.refresh_child_card_recommendation()

@router.put("/child/pop_last_card", response_model=CardSelectionResult)
async def _pop_last_child_card(
        session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]) -> CardSelectionResult:
    
    selection, recommendation = await session.pop_last_child_card()
    interim_cards = await session.get_card_info_from_identities(selection.cards)

    return CardSelectionResult(interim_cards=interim_cards, new_recommendation=recommendation)


@router.post("/child/confirm_cards", response_model=ResponseWithTurnId[ParentGuideRecommendationResult])
async def confirm_child_card_selection(
        session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]) -> ResponseWithTurnId[ParentGuideRecommendationResult]:
    turn, recommendation = await session.confirm_child_card_selection()
    return ResponseWithTurnId[ParentGuideRecommendationResult](next_turn_id=turn.id, payload=recommendation)
