from io import BytesIO
from typing import Annotated
from fastapi import APIRouter, Depends, Response
from fastapi.responses import FileResponse
import pendulum
from sqlmodel.ext.asyncio.session import AsyncSession
from zipfile import ZipFile, ZIP_DEFLATED

from py_core.config import AACessTalkConfig
from py_database.model import DyadORM
from backend.crud.dyad.session import make_user_dataset_table, make_dataset_table_all_dyads
from backend.database import with_db_session


router = APIRouter()


@router.get("/db/download")
async def _download_db():
    return FileResponse(
        path=AACessTalkConfig.database_file_path,
        media_type="application/octet-stream"
    )

@router.get("/export/all")
async def _export_data_all(db: Annotated[AsyncSession, Depends(with_db_session)]):
        
    session_table, turn_table = await make_dataset_table_all_dyads(db)

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w', ZIP_DEFLATED) as zip_file:
        session_table_buff = BytesIO()
        session_table.to_csv(session_table_buff, index=False)
        zip_file.writestr(f"sessions-all.csv", session_table_buff.getvalue())

        turn_table_buff = BytesIO()
        turn_table.to_csv(turn_table_buff, index=False)
        zip_file.writestr(f"turns-all.csv", turn_table_buff.getvalue())
    
    zip_buffer.seek(0)

    dt = pendulum.now().format("YYYY-MM-DD-HH-mm-ss")

    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/x-zip-compressed"
    )


@router.get("/export/{dyad_id}")
async def _export_data_of_dyad(dyad_id: str, db: Annotated[AsyncSession, Depends(with_db_session)]):
    
    dyad = await db.get(DyadORM, dyad_id)

    print(dyad_id, dyad)
    
    session_table, turn_table = await make_user_dataset_table(dyad_id, db)

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w', ZIP_DEFLATED) as zip_file:
        session_table_buff = BytesIO()
        session_table.to_csv(session_table_buff, index=False)
        zip_file.writestr(f"sessions-{dyad.alias}.csv", session_table_buff.getvalue())

        turn_table_buff = BytesIO()
        turn_table.to_csv(turn_table_buff, index=False)
        zip_file.writestr(f"turns-{dyad.alias}.csv", turn_table_buff.getvalue())
    
    zip_buffer.seek(0)

    dt = pendulum.now().format("YYYY-MM-DD-HH-mm-ss")

    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/x-zip-compressed"
    )