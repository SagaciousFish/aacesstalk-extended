
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from py_core.system.model import FreeTopicDetail
from py_core.system.storage import UserStorage

from backend.routers.dyad.common import FreeTopicDetailInfo, get_user_storage


router = APIRouter()

class FreeTopicDetailsResult(BaseModel):
    dyad_id: str
    details: list[FreeTopicDetailInfo]

@router.get('/freetopics', response_model=FreeTopicDetailsResult)
async def get_free_topic_details(user_storage: Annotated[UserStorage, Depends(get_user_storage)]):
    details = await user_storage.get_free_topic_details()
    print("details: ", details)
    return FreeTopicDetailsResult(
        dyad_id=user_storage.user_id,
        details = [FreeTopicDetailInfo(**detail.model_dump(exclude={"topic_image_filename"})) for detail in details]
    )