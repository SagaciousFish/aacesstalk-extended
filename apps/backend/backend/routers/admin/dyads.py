from os import path
from typing import Annotated, Optional, Union
from fastapi import APIRouter, Depends, Form, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from py_core.system.model import Dyad, FreeTopicDetail, Dialogue, UserDefinedCardInfo, CardCategory, DialogueRole
from py_core.system.storage import UserStorage
from py_database.model import DyadORM, UserDefinedCardInfoORM, DialogueTurnORM
from backend.crud.dyad.account import create_dyad
from backend.crud.dyad.session import DialogueSession, ExtendedSessionInfo, get_dialogue, get_session_summaries
from backend.crud.media import get_free_topic_image, process_uploaded_image
from backend.database import with_db_session
from backend.database.models import DyadLoginCode
from backend.routers.admin.common import check_admin_credential
from backend.routers.dyad.common import get_user_storage_with_id
from py_core.config import AACessTalkConfig
from py_database.model import FreeTopicDetailORM
from chatlib.utils.time import get_timestamp
from math import floor
from os import remove


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
    return await get_free_topic_image(detail_id, user_storage)

@router.post("/{dyad_id}/freetopics", response_model=FreeTopicDetail)
async def _create_free_topic_detail(dyad_id: str, db: Annotated[AsyncSession, Depends(with_db_session)], topic: Annotated[str, Form()], description: Annotated[str, Form()], image: Union[UploadFile, None] = None):
    
    orm = FreeTopicDetailORM(dyad_id=dyad_id, subtopic=topic, subtopic_description=description, topic_image_filename=None)
        
    if image is not None:
        local_filename = f"{orm.id}_{floor(get_timestamp()/1000)}.png"
        local_file_path = path.join(AACessTalkConfig.get_free_topic_image_dir_path(dyad_id, True), local_filename)

        await process_uploaded_image(image, local_file_path)
        
        orm.topic_image_filename = local_filename
    
    db.add(orm)
    await db.commit()
    await db.refresh(orm)
    
    return orm.to_data_model()


@router.put("/{dyad_id}/freetopics/{detail_id}", response_model=FreeTopicDetail)
async def _update_free_topic_detail(dyad_id: str, detail_id: str, db: Annotated[AsyncSession, Depends(with_db_session)], 
                                   topic: Union[str, None] = Form(None), 
                                   description: Union[str, None] = Form(None), remove_image: Union[bool, None] = Form(None), image: Union[UploadFile, None] = None):
    
    orm = await db.get(FreeTopicDetailORM, detail_id)
    if orm is not None:    
            if image is not None:
                local_filename = f"{orm.id}_{floor(get_timestamp()/1000)}.png"
                local_file_path = path.join(AACessTalkConfig.get_free_topic_image_dir_path(dyad_id, True), local_filename)

                await process_uploaded_image(image, local_file_path)
                
                orm.topic_image_filename = local_filename
            elif remove_image is True:
                remove(path.join(AACessTalkConfig.get_free_topic_image_dir_path(dyad_id, True), orm.topic_image_filename))
                orm.topic_image_filename = None

            if topic is not None:
                orm.subtopic = topic
                
            if description is not None:
                orm.subtopic_description = description

            db.add(orm)
            await db.commit()
            await db.refresh(orm)
            
            return orm.to_data_model()
    else:
            raise HTTPException(404)
    

@router.get("/{dyad_id}/sessions", response_model=list[ExtendedSessionInfo])
async def _get_sessions(dyad_id: str, db: Annotated[AsyncSession, Depends(with_db_session)]):
    return await get_session_summaries(dyad_id, db, includeOnlyTerminated=False)


@router.get("/{dyad_id}/dialogues/{session_id}", response_model=DialogueSession)
async def _get_sessions(dyad_id: str, session_id: str, db: Annotated[AsyncSession, Depends(with_db_session)]):
    return await get_dialogue(session_id, db)

@router.get("/{dyad_id}/dialogues/{session_id}/{turn_id}/audio", response_class=FileResponse)
async def _get_turn_audio(dyad_id: str, session_id: str, turn_id: str, db: Annotated[AsyncSession, Depends(with_db_session)]):
    turn_info = await db.get(DialogueTurnORM, turn_id)
    if turn_info is not None:
        if turn_info.role == DialogueRole.Parent:
            if turn_info.audio_filename is not None:
                file_path = path.join(AACessTalkConfig.get_turn_audio_recording_dir_path(dyad_id, False), turn_info.audio_filename)
                return FileResponse(file_path, filename=turn_info.audio_filename, media_type="audio/m4a")
            else:
                raise HTTPException(status.HTTP_400_BAD_REQUEST)
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

@router.get("/{dyad_id}/custom_cards", response_model=list[UserDefinedCardInfo])
async def _get_user_defined_cards(dyad_id: str, user_storage: Annotated[UserStorage, Depends(get_user_storage_with_id)]):
    return await user_storage.get_user_defined_cards()

@router.post("/{dyad_id}/custom_cards/new", response_model=UserDefinedCardInfo)
async def _add_user_defined_card(dyad_id: str, image: UploadFile, label_localized: Annotated[str, Form()], 
                                 category: Annotated[CardCategory, Form()], 
                                 user_storage: Annotated[UserStorage, Depends(get_user_storage_with_id)],
                                 label: Union[str, None] = Form(None)):
    info = UserDefinedCardInfoORM(dyad_id=dyad_id, label=label, label_localized=label_localized, category=category, image_filename=None, image_width=512, image_height=512)
    filename = f"{info.id}_{floor(get_timestamp()/1000)}.png"
    info.image_filename = filename

    filepath = path.join(AACessTalkConfig.get_user_defined_card_dir_path(dyad_id, True), filename)
    await process_uploaded_image(image, filepath)

    await user_storage.register_user_defined_card(info.to_data_model())
    return info

@router.get("/{dyad_id}/custom_cards/{card_id}/image", response_class=FileResponse)
async def _get_custom_card_image(dyad_id: str, card_id: str, user_storage: Annotated[UserStorage, Depends(get_user_storage_with_id)]):
    info = await user_storage.get_user_defined_card(card_id)
    if info.image_filename is not None:
        image_path = path.join(AACessTalkConfig.get_user_defined_card_dir_path(dyad_id, True), info.image_filename)
        if path.exists(image_path):
            return FileResponse(image_path, media_type="image/png") 

@router.delete("/{dyad_id}/custom_cards/{card_id}")
async def _remove_custom_card(dyad_id: str, card_id: str, user_storage: Annotated[UserStorage, Depends(get_user_storage_with_id)]):
    info = await user_storage.get_user_defined_card(card_id)
    if info.image_filename is not None:
        image_path = path.join(AACessTalkConfig.get_user_defined_card_dir_path(dyad_id, True), info.image_filename)
        if path.exists(image_path):
            remove(image_path)
    await user_storage.remove_user_defined_card(card_id)
    
    