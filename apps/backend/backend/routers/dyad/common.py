from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend import env_variables
from backend.crud.dyad.account import get_dyad_by_id
from backend.database import get_db_session, AsyncSession
from py_database.model import Dyad
from jose import JWTError, jwt
from chatlib.utils.env_helper import get_env_variable

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
