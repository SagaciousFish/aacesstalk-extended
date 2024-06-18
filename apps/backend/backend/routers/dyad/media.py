import select
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from py_core.system.model import CardIdentity
from backend.database import with_db_session
from py_database.database import AsyncSession
from py_database.model import DyadORM, ChildCardRecommendationResultORM
from sqlmodel import select
from py_core.utils.tts.clova_voice import ClovaVoice, ClovaVoiceParams

from backend.routers.dyad.common import get_signed_in_dyad_orm


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