from typing import Annotated, Optional
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from py_core.system.model import Dyad, FreeTopicDetail
from py_core.system.storage import UserStorage
from py_database.model import DyadORM
from backend.crud.dyad.account import create_dyad
from backend.crud.media import get_free_topic_image
from backend.database import with_db_session
from backend.database.models import DyadLoginCode
from backend.routers.admin.common import check_admin_credential
from backend.routers.dyad.common import get_user_storage_with_id


router = APIRouter(dependencies=[Depends(check_admin_credential)])

class DyadWithPasscode(Dyad):
    passcode: str

class DyadUpdateArgs(BaseModel):
    passcode: Optional[str] = None
    alias: Optional[str] = None
    child_name: Optional[str] = None
    parent_type: Optional[str] = None
    child_gender: Optional[str] = None


class DyadsResult(BaseModel):
    dyads: list[DyadWithPasscode]

@router.get("/all", response_model=DyadsResult)
async def get_all_dyads(db: Annotated[AsyncSession, Depends(with_db_session)]):
    result = await db.exec((select(DyadORM, DyadLoginCode)
                 .where(DyadLoginCode.active == True)
                 .where(DyadLoginCode.dyad_id == DyadORM.id)))
    dyads = [DyadWithPasscode(**dyad_orm.model_dump(), passcode=code_orm.code) for dyad_orm, code_orm in result]
    return DyadsResult(dyads=dyads)

@router.get("/{dyad_id}", response_model=DyadWithPasscode)
async def get_dyad_by_id(dyad_id: str, db: Annotated[AsyncSession, Depends(with_db_session)]):
    result = await db.exec((select(DyadORM, DyadLoginCode)
                .where(DyadORM.id == dyad_id)
                .where(DyadLoginCode.active == True)
                .where(DyadLoginCode.dyad_id == DyadORM.id)))
    orm, logincode = result.first()
    return DyadWithPasscode(**orm.model_dump(), passcode=logincode.code)



@router.put("/{dyad_id}", response_model=DyadORM)
async def update_dyad(dyad_id: str, update: DyadUpdateArgs, db: Annotated[AsyncSession, Depends(with_db_session)]):
    async with db.begin():
        dyad = await db.get(DyadORM, dyad_id)
        if dyad is not None:
            dyad.sqlmodel_update(update.model_dump(exclude_unset=True, exclude_none=True))
            db.add(dyad)
            await db.commit()
            await db.refresh(dyad)
            return dyad

class DyadCreateArgs(BaseModel):
    alias: str = None
    child_name: str = None
    parent_type: str = None
    child_gender: str = None   
    
@router.post("/new", response_model=DyadWithPasscode)
async def _create_dyad(args:DyadCreateArgs, db: Annotated[AsyncSession, Depends(with_db_session)]):
    dyad_orm, logincode = await create_dyad(**args.model_dump(), session=db)
    return DyadWithPasscode(**dyad_orm.model_dump(), passcode=logincode.code)

class FreeTopicDetailsResult(BaseModel):
    dyad_id: str
    details: list[FreeTopicDetail]

@router.get("/{dyad_id}/freetopics", response_model=FreeTopicDetailsResult)
async def get_free_topic_details(dyad_id: str, user_storage: Annotated[UserStorage, Depends(get_user_storage_with_id)]):
    details = await user_storage.get_free_topic_details()
    print("details: ", details)
    return FreeTopicDetailsResult(
        dyad_id=dyad_id,
        details = details
    )

@router.delete('/{dyad_id}/freetopics/{detail_id}')
async def remove_free_topic(detail_id: str, user_storage: Annotated[UserStorage, Depends(get_user_storage_with_id)]):
    await user_storage.remove_free_topic_detail(detail_id)

@router.get('/{dyad_id}/freetopics/{detail_id}/image', response_class=FileResponse)
async def _get_free_topic_image(detail_id: str, user_storage: Annotated[UserStorage, Depends(get_user_storage_with_id)]):
    return get_free_topic_image(detail_id, user_storage)