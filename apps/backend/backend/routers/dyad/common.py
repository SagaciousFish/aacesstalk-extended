from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend import env_variables
from backend.crud.dyad.account import get_dyad_by_id
from backend.crud.dyad.session import find_session_orm
from backend.database import with_db_session, AsyncSession, engine
from py_database.model import Dyad, Session as SessionORM
from jose import JWTError, jwt
from chatlib.utils.env_helper import get_env_variable


from typing import Annotated
from py_database import SQLSessionStorage
from py_database.database import get_async_session
from py_core.system.moderator import ModeratorSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_signed_in_dyad_orm(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(with_db_session)]) -> Dyad:
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


async def retrieve_moderator_session(session_id: str, dyad_orm: Annotated[Dyad, Depends(get_signed_in_dyad_orm)]):
    print("Retrieve moderator session...")
    if session_id in sessions:
        session = sessions[session_id]
        session.storage = await SQLSessionStorage.restore_instance(session_id, lambda: get_async_session(engine))
        return session
    else:
        async with get_async_session(engine) as db:
            session_info_orm = await find_session_orm(session_id, dyad_orm.id, db)
            
            session = ModeratorSession(dyad_orm.to_data_model(), SQLSessionStorage(lambda: get_async_session(engine), session_info_orm.to_data_model()))
            sessions[session_id] = session
            return session