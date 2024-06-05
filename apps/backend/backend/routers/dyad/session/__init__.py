from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from backend.database import with_db_session, AsyncSession
from backend.routers.dyad.common import get_signed_in_dyad_orm, retrieve_moderator_session
from backend.crud.dyad.session import create_moderator_session, end_session, find_session_orm
from py_database.model import Dyad, Session as SessionORM
from py_core.system.session_topic import SessionTopicInfo
from py_core.system import ModeratorSession
from sqlmodel import delete

from . import message

router = APIRouter()

router.include_router(message.router, prefix="/{session_id}/message")

@router.get("{session_id}/info", response_model=SessionORM)
async def _get_session_info(session_id: str, dyad: Annotated[Dyad, Depends(get_signed_in_dyad_orm)], db: Annotated[AsyncSession, Depends(with_db_session)]) -> SessionORM | None:

    s = await find_session_orm(session_id, dyad.id, db)
    if s is not None:
        return s
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")

class SessionInitiationArgs(BaseModel):
    topic: SessionTopicInfo
    timezone: str

@router.post("/new")
async def _initiate_session(req: Request, dyad: Annotated[Dyad, Depends(get_signed_in_dyad_orm)],
                               db: Annotated[AsyncSession, Depends(with_db_session)]) -> str:
    args = SessionInitiationArgs(**(await req.json()))
    new_session = await create_moderator_session(dyad, args.topic, args.timezone, db)
    return new_session.id

@router.delete("/{session_id}/abort")
async def _abort_session(session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)], 
                        dyad: Annotated[Dyad, Depends(get_signed_in_dyad_orm)],
                        db: Annotated[AsyncSession, Depends(with_db_session)]):
    try:
        session.cancel_all_async_tasks()
        await session.storage.delete_entities()
        db.exec(delete(SessionORM).where(SessionORM.id == session.storage.session_id))
        
    except ValueError as ex:
        print(ex)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")


@router.put("/{session_id}/end")
async def _end_session(session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)], dyad: Annotated[Dyad, Depends(get_signed_in_dyad_orm)],
                      db: Annotated[AsyncSession, Depends(with_db_session)]):
    try:
        session.cancel_all_async_tasks()
        await end_session(session.storage.session_id, dyad.id, db)
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")
