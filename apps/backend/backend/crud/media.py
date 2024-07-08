from py_core.system.storage import UserStorage
from os import path
from fastapi.responses import FileResponse
from py_core.system.storage import UserStorage
from py_core.config import AACessTalkConfig


async def get_free_topic_image(detail_id: str, user_storage: UserStorage):
    detail = await user_storage.get_free_topic_detail(detail_id)
    if detail is not None and detail.topic_image_filename is not None:
        image_path = path.join(AACessTalkConfig.get_free_topic_image_dir_path(user_storage.user_id, make_if_not_exist=True), detail.topic_image_filename)
        if path.exists(image_path):
            return FileResponse(image_path)