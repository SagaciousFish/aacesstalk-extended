from typing import Annotated

from fastapi import APIRouter, Depends, Header
from backend.database import get_db_session, AsyncSession
from backend.routers.dyad.common import depends_auth_dyad
from backend.crud.dyad.session import create_moderator_session, end_session
from py_database.model import Dyad

router = APIRouter()


@router.post("/new")
async def initiate_session(timezone: Annotated[str, Header()], dyad: Annotated[Dyad, depends_auth_dyad],
                               db: Annotated[AsyncSession, Depends(get_db_session)]) -> str:
    new_session = await create_moderator_session(dyad, timezone, db)
    return new_session.id


@router.put("/{session_id}/end")
async def end_session(session_id: str, dyad: Annotated[Dyad, depends_auth_dyad],
                      db: Annotated[AsyncSession, Depends(get_db_session)]):
    await end_session(session_id, dyad.id, db)
