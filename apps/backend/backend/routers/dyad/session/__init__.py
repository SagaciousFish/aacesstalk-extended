from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from backend.database import get_db_session, AsyncSession
from backend.routers.dyad.common import get_signed_in_dyad
from backend.crud.dyad.session import abort_session, create_moderator_session, end_session, find_session_orm
from py_database.model import Dyad, Session
from py_core.system.session_topic import SessionTopicInfo

from . import message

router = APIRouter()

router.include_router(message.router, prefix="/{session_id}/message")

@router.get("{session_id}/info", response_model=Session)
async def _get_session_info(session_id: str, dyad: Annotated[Dyad, Depends(get_signed_in_dyad)], db: Annotated[AsyncSession, Depends(get_db_session)]) -> Session | None:

    s = await find_session_orm(session_id, dyad.id, db)
    if s is not None:
        return s
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")

class SessionInitiationArgs(BaseModel):
    topic: SessionTopicInfo
    timezone: str

@router.post("/new")
async def _initiate_session(req: Request, dyad: Annotated[Dyad, Depends(get_signed_in_dyad)],
                               db: Annotated[AsyncSession, Depends(get_db_session)]) -> str:
    args = SessionInitiationArgs(**(await req.json()))
    new_session = await create_moderator_session(dyad, args.topic, args.timezone, db)
    return new_session.id

@router.delete("/{session_id}/abort")
async def _abort_session(session_id: str, dyad: Annotated[Dyad, Depends(get_signed_in_dyad)],
                      db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        await abort_session(session_id, dyad.id, db)
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")


@router.put("/{session_id}/end")
async def _end_session(session_id: str, dyad: Annotated[Dyad, Depends(get_signed_in_dyad)],
                      db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        await end_session(session_id, dyad.id, db)
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")
