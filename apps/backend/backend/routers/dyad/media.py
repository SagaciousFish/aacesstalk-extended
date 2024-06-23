from os import path
from time import perf_counter
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from py_core.system.model import CardIdentity
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


class CardImageMatchingResult:
    matchings: list[CardImageMatching]

@router.get('/match_card_images/{recommendation_id}', response_class=CardImageMatchingResult)
async def match_card_images(recommendation_id: str, db: Annotated[AsyncSession, Depends(with_db_session)], image_matcher: Annotated[CardImageMatcher, Depends(get_card_image_matcher)]):
    t_start = perf_counter()
    card_recommendation = await db.get(ChildCardRecommendationResultORM, recommendation_id)
    matches = await image_matcher.match_card_images(card_recommendation.cards)
    t_end = perf_counter()
    print(f"Card matching took {t_end} sec.")
    return CardImageMatchingResult(matchinggs=matches)

@router.get('/card_image', response_class=FileResponse)
async def get_card_image(type: CardType, image_id: str, image_matcher: Annotated[CardImageMatcher, Depends(get_card_image_matcher)]):
    image_path = await image_matcher.get_card_image_filepath(type, image_id)
    if path.exists(image_path):
        return FileResponse(image_path)