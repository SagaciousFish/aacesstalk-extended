from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from backend.database import get_db_session, AsyncSession
from backend.routers.dyad.common import depends_auth_dyad
from backend.crud.dyad.session import create_moderator_session, end_session, find_session
from py_database.model import Dyad, Session

from . import message

router = APIRouter()

router.include_router(message.router, prefix="/{session_id}/message")

@router.get("{session_id}/info", response_model=Session)
async def get_session_info(session_id: str, dyad: Annotated[Dyad, depends_auth_dyad], db: Annotated[AsyncSession, Depends(get_db_session)]) -> Session | None:

    s = await find_session(session_id, dyad.id, db)
    if s is not None:
        return s
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")


@router.post("/new")
async def initiate_session(timezone: Annotated[str, Header()], dyad: Annotated[Dyad, depends_auth_dyad],
                               db: Annotated[AsyncSession, Depends(get_db_session)]) -> str:
    new_session = await create_moderator_session(dyad, timezone, db)
    return new_session.id


@router.put("/{session_id}/end")
async def end_session(session_id: str, dyad: Annotated[Dyad, depends_auth_dyad],
                      db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        await end_session(session_id, dyad.id, db)
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")
