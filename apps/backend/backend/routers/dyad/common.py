from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from backend import env_variables
from backend.crud.dyad.account import get_dyad_by_id
from backend.database import with_db_session, AsyncSession, db_sessionmaker
from py_database.model import DyadORM, SessionORM as SessionORM
import jwt
from chatlib.utils.env_helper import get_env_variable


from typing import Annotated
from py_database.database import make_async_session_maker
from py_database import SQLSessionStorage, SQLUserStorage
from py_core.system.moderator import ModeratorSession
from py_core.system.storage import UserStorage
from py_core.system.task.card_image_matching.card_image_matcher import CardImageMatcher 
from py_core.system.model import Dyad, SessionTopicInfo, id_generator


class FreeTopicDetailInfo(BaseModel):
    id: str
    subtopic: str
    subtopic_description: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_signed_in_dyad_orm(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(with_db_session)]) -> DyadORM:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, get_env_variable(env_variables.AUTH_SECRET), algorithms=['HS256'])
        dyad_id: str = payload.get("sub")
        if dyad_id is None:
            raise credentials_exception

    except jwt.exceptions.DecodeError as ex:
        print(ex)
        raise credentials_exception

    dyad = await get_dyad_by_id(dyad_id, db)

    if dyad is None:
        raise credentials_exception
    else:
        return dyad


sessions: dict[str, ModeratorSession] = {}

SQLSessionStorage.set_session_maker(db_sessionmaker)
SQLUserStorage.set_session_maker(db_sessionmaker)

@lru_cache(maxsize=20)
def get_user_storage_with_id(dyad_id: str)->SQLUserStorage:
    return SQLUserStorage(dyad_id)

@lru_cache(maxsize=20)
def _get_card_image_matcher(dyad_id: str) -> CardImageMatcher:
    return CardImageMatcher(get_user_storage_with_id(dyad_id))

def get_card_image_matcher(dyad_orm: Annotated[DyadORM, Depends(get_signed_in_dyad_orm)]) -> CardImageMatcher:
    return _get_card_image_matcher(dyad_orm.id)

def get_user_storage(dyad_orm: Annotated[DyadORM, Depends(get_signed_in_dyad_orm)]) -> UserStorage:
    return get_user_storage_with_id(dyad_orm.id)
            
async def create_moderator_session(dyad: Dyad, topic: SessionTopicInfo, timezone: str) -> ModeratorSession:
    return await ModeratorSession.create(dyad, topic, timezone, SQLSessionStorage(id_generator()))

async def retrieve_moderator_session(session_id: str, dyad_orm: Annotated[DyadORM, Depends(get_signed_in_dyad_orm)]):
    print("Retrieve moderator session...")
    if session_id in sessions:
        session = sessions[session_id]
        session.storage = await SQLSessionStorage.restore_instance(session_id)
        return session
    else:
        storage = await SQLSessionStorage.restore_instance(session_id)
        session = await ModeratorSession.restore_instance(dyad_orm.to_data_model(), storage)
        sessions[session_id] = session
        return session

async def dispose_session_instance(session_id: str):
    if session_id in sessions:
        await sessions[session_id].storage.dispose()
        sessions.__delitem__(session_id)