from typing import Annotated, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from py_core.system.model import Dyad
from py_database.model import DyadORM
from backend.crud.dyad.account import create_dyad
from backend.database import with_db_session
from backend.database.models import DyadLoginCode
from backend.routers.admin.common import check_admin_credential


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