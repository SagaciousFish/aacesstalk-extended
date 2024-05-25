import asyncio
from enum import StrEnum
from typing import AsyncGenerator, Union, Literal

from nanoid import generate
from pydantic import BaseModel, Field

from py_core.system.model import CardInfo, UserDefinedCardInfo
from py_core.system.storage import UserStorage
from py_core.system.task.card_image_matching.card_image_db_retriever import CardImageDBRetriever

from py_core.utils.models import CardImageInfo


class CardType(StrEnum):
    stock = "stock"
    custom = "custom"


class CardImageMatching(BaseModel):
    id: str = Field(default_factory=lambda: generate(5))
    card_info_id: str
    type: CardType
    image_id: str


class CardImageMatcher:
    def __init__(self, user_storage: UserStorage):
        self.__user_storage = user_storage
        self.__db_retriever = CardImageDBRetriever()

    async def match_card_images(self, card_info_list: list[CardInfo]) -> AsyncGenerator[CardImageMatching, None]:
        async def get_card_matching(card_info: CardInfo):
            custom_card_query_result = await self.__user_storage.query_user_defined_card(card_info.category, card_info.label_localized)
            if custom_card_query_result is not None:
                return CardImageMatching(card_info_id=card_info.id, type=CardType.custom, image_id=custom_card_query_result.id)
            else:
                db_card_image_infos: list[CardImageInfo] = await self.__db_retriever.query_nearest_card_image_infos(card_info.label, k=1)
                if len(db_card_image_infos) > 0:
                    return CardImageMatching(card_info_id=card_info.id, type=CardType.stock, image_id=db_card_image_infos[0].id)

        for completed_matching in asyncio.as_completed([get_card_matching(info) for info in card_info_list]):
            yield await completed_matching
