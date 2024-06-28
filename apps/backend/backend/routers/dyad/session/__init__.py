from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from backend.database import with_db_session, AsyncSession
from backend.routers.dyad.common import create_moderator_session, dispose_session_instance, get_signed_in_dyad_orm, retrieve_moderator_session
from backend.crud.dyad.session import find_session_orm
from py_database.model import DyadORM, SessionORM as SessionORM
from py_core.system.session_topic import SessionTopicInfo
from py_core.system import ModeratorSession
from sqlmodel import delete
from py_core.system.model import ParentGuideRecommendationResult

from . import message

router = APIRouter()

router.include_router(message.router, prefix="/{session_id}/message")

@router.get("{session_id}/info", response_model=SessionORM)
async def _get_session_info(session_id: str, dyad: Annotated[DyadORM, Depends(get_signed_in_dyad_orm)], db: Annotated[AsyncSession, Depends(with_db_session)]) -> SessionORM | None:

    s = await find_session_orm(session_id, dyad.id, db)
    if s is not None:
        return s
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")

class SessionInitiationArgs(BaseModel):
    topic: SessionTopicInfo
    timezone: str

@router.post("/new")
async def _initiate_session(req: Request, dyad: Annotated[DyadORM, Depends(get_signed_in_dyad_orm)]) -> str:
    args = SessionInitiationArgs(**(await req.json()))
    new_session = await create_moderator_session(dyad.to_data_model(), args.topic, args.timezone)
    return new_session.storage.session_id

class SessionStartResult(BaseModel):
    parent_guides: ParentGuideRecommendationResult
    turn_id: str

@router.post("/{session_id}/start", response_model=SessionStartResult)
async def _start_session(
    session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)])->SessionStartResult:

    turn, guides = await session.start()
    return SessionStartResult(parent_guides=guides, turn_id=turn.id)

@router.delete("/{session_id}/abort")
async def _abort_session(session_id: str, session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)],
                         dyad: Annotated[DyadORM, Depends(get_signed_in_dyad_orm)],
                         db: Annotated[AsyncSession, Depends(with_db_session)]):
    try:
        session.cancel_all_async_tasks()
        await session.storage.delete_entities()
        session_orm = await find_session_orm(session_id, dyad.id, db)
        await db.delete(session_orm)
        await dispose_session_instance(session_id)

    except ValueError as ex:
        print(ex)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")


@router.put("/{session_id}/end")
async def _end_session(session_id: str, session: Annotated[ModeratorSession, Depends(retrieve_moderator_session)]):
    try:
        await session.terminate()
        await dispose_session_instance(session_id)
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No session with the id and the corresponding dyad.")
