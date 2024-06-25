from os import path
from time import perf_counter
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from py_core.system.model import CardIdentity
from pydantic import BaseModel
from backend.database import with_db_session
from py_database.database import AsyncSession
from py_database.model import DyadORM, ChildCardRecommendationResultORM
from sqlmodel import select
from py_core.utils.tts.clova_voice import ClovaVoice, ClovaVoiceParams
from py_core.system.task.card_image_matching import CardType, CardImageMatcher, CardImageMatching

from backend.routers.dyad.common import get_card_image_matcher, get_signed_in_dyad_orm


router = APIRouter()

voice_engine = ClovaVoice()

voice_default_params = ClovaVoiceParams()


@router.get("/voiceover", response_class=FileResponse)
async def get_voiceover(card_id: str, recommendation_id: str, 
                        dyad_orm: Annotated[DyadORM, Depends(get_signed_in_dyad_orm)], 
                        db: Annotated[AsyncSession, Depends(with_db_session)]):
       
    result = await db.get(ChildCardRecommendationResultORM, recommendation_id)
    if result is not None:
        recommendation = result.to_data_model()
        card = recommendation.find_card_by_id(card_id)
        if card is not None:
            return FileResponse(await voice_engine.create_voice(card.label_localized, voice_default_params))

    raise HTTPException(status_code=400, detail="NoSuchCard")


class CardImageMatchingResult(BaseModel):
    matchings: list[CardImageMatching]

@router.get('/match_card_images/{recommendation_id}', response_model=CardImageMatchingResult)
async def match_card_images(recommendation_id: str, db: Annotated[AsyncSession, Depends(with_db_session)], dyad_orm: Annotated[DyadORM, Depends(get_signed_in_dyad_orm)], image_matcher: Annotated[CardImageMatcher, Depends(get_card_image_matcher)]):
    t_start = perf_counter()
    card_recommendation = await db.get(ChildCardRecommendationResultORM, recommendation_id)
    card_recommendation = card_recommendation.to_data_model()
    matches = await image_matcher.match_card_images(card_recommendation.cards, dyad_orm.parent_type, dyad_orm.child_gender)
    t_end = perf_counter()
    print(f"Card matching took {t_end - t_start} sec.")
    return CardImageMatchingResult(matchings=matches)

@router.get('/card_image', response_class=FileResponse)
async def get_card_image(card_type: CardType, image_id: str, dyad_orm: Annotated[DyadORM, Depends(get_signed_in_dyad_orm)], image_matcher: Annotated[CardImageMatcher, Depends(get_card_image_matcher)]):
    image_path = await image_matcher.get_card_image_filepath(card_type, image_id, dyad_orm.parent_type, dyad_orm.child_gender)
    if path.exists(image_path):
        return FileResponse(image_path)