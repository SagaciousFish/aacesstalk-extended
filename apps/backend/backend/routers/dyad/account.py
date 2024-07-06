from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.crud.dyad import account
from backend.database import with_db_session
from py_database.database import AsyncSession

from backend.routers.dyad.common import get_user_storage
from backend.routers.dyad.data import FreeTopicDetailInfo
from backend.routers.errors import ErrorType

router = APIRouter()


class LoginCodeCredential(BaseModel):
    code: str

class AuthenticationResult(BaseModel):
    jwt: str
    free_topics: list[FreeTopicDetailInfo]

@router.post("/login", response_model=AuthenticationResult)
async def login_with_code(credential: LoginCodeCredential, session: Annotated[AsyncSession, Depends(with_db_session)]):
    try:
        jwt, dyad = await account.login_with_code(credential.code, session)
        free_topic_details = await get_user_storage(dyad).get_free_topic_details()
        return AuthenticationResult(jwt=jwt, free_topics=[FreeTopicDetailInfo(**d.model_dump(exclude={"topic_image_filename"})) for d in free_topic_details])
    except ValueError as ex:
        print(ex)
        raise HTTPException(status_code=400, detail=ErrorType.NoSuchUser)