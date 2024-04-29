from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.crud.dyad import account
from backend.database import get_db_session
from py_database.database import AsyncSession

router = APIRouter()


class LoginCodeCredential(BaseModel):
    code: str


@router.post("/login", response_model=str)
async def login_with_code(credential: LoginCodeCredential, session: AsyncSession = Depends(get_db_session)) -> str:
    try:
        await account.login_with_code(credential.code, session)
    except ValueError:
        raise HTTPException(status_code=400, detail="NoSuchUser")
