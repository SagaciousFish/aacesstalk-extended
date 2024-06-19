from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend import env_variables
from backend.crud.dyad.account import get_dyad_by_id
from backend.database import with_db_session, AsyncSession, db_sessionmaker
from py_database.model import DyadORM, SessionORM as SessionORM
from jose import JWTError, jwt
from chatlib.utils.env_helper import get_env_variable


from typing import Annotated
from py_database.database import make_async_session_maker
from py_database.storage import SQLSessionStorage
from py_core.system.moderator import ModeratorSession
from py_core.system.model import Dyad, SessionTopicInfo, id_generator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_signed_in_dyad_orm(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(with_db_session)]) -> DyadORM:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    print("Try get signed_in dyad.")

    try:
        payload = jwt.decode(token, get_env_variable(env_variables.AUTH_SECRET))
        dyad_id: str = payload.get("sub")
        if dyad_id is None:
            raise credentials_exception

    except JWTError as ex:
        print(ex)
        raise credentials_exception

    dyad = await get_dyad_by_id(dyad_id, db)

    if dyad is None:
        raise credentials_exception
    else:
        print("Successfully found a signed-in dyad.")
        return dyad


sessions: dict[str, ModeratorSession] = {}

SQLSessionStorage.set_session_maker(db_sessionmaker)
            
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