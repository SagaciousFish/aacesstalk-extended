from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend import env_variables
from backend.crud.dyad.account import get_dyad_by_id
from backend.crud.dyad.session import find_session_orm
from backend.database import get_db_session, AsyncSession
from py_database.model import Dyad, Session as SessionORM
from jose import JWTError, jwt
from chatlib.utils.env_helper import get_env_variable


from typing import Annotated
from py_database import SQLSessionStorage
from py_core.system.moderator import ModeratorSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_signed_in_dyad(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db_session)]) -> Dyad:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, get_env_variable(env_variables.AUTH_SECRET))
        dyad_id: str = payload.get("sub")
        if dyad_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    dyad = await get_dyad_by_id(dyad_id, db)

    if dyad is None:
        raise credentials_exception
    else:
        return dyad


def depends_auth_dyad() -> Dyad:
    return Depends(get_signed_in_dyad)


sessions: dict[str, ModeratorSession] = {}


async def retrieve_moderator_session(session_id: str, dyad: Annotated[Dyad, depends_auth_dyad], db: Annotated[AsyncSession, Depends(get_db_session)]):
    if session_id in sessions:
        session = sessions[session_id]
        session.storage = SQLSessionStorage.restore_instance(session_id, db)
        return session
    else:
        session_info_orm = await find_session_orm(session_id, dyad.id, db)
        
        session = ModeratorSession(dyad, SQLSessionStorage(db, session_info_orm.to_data_model()))
        sessions[session_id] = session
        return session