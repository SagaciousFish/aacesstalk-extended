from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from chatlib.utils.env_helper import get_env_variable

from backend.env_variables import ADMIN_ID, AUTH_SECRET


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def check_admin_credential(token: Annotated[str, Depends(oauth2_scheme)])->bool:
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin authorization header",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, get_env_variable(AUTH_SECRET), algorithms=['HS256'])
        admin_id = payload.get("sub")
        if admin_id == get_env_variable(ADMIN_ID):
            return True
        else:
            raise exception
    except jwt.exceptions.DecodeError as ex:
        raise exception from ex