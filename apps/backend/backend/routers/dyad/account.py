from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.crud.dyad import account
from backend.database import with_db_session
from py_database.database import AsyncSession

router = APIRouter()


class LoginCodeCredential(BaseModel):
    code: str

class AuthenticationResult(BaseModel):
    jwt: str

@router.get('/ping')
def ping():
    return 'Dyad account router working.'

@router.post("/login", response_model=AuthenticationResult)
async def login_with_code(credential: LoginCodeCredential, session: Annotated[AsyncSession, Depends(with_db_session)]):
    try:
        jwt = await account.login_with_code(credential.code, session)
        return AuthenticationResult(jwt=jwt)
    except ValueError:
        raise HTTPException(status_code=400, detail="NoSuchUser")
