from enum import StrEnum
from typing import AsyncGenerator, Union, Literal

from nanoid import generate
from pydantic import BaseModel, Field

from py_core.system.model import CardInfo, UserDefinedCardInfo
from py_core.system.storage import UserStorage
from py_core.system.task.card_image_matching.card_image_db_retriever import CardImageDBRetriever


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
        self.__user_storage.query_user_defined_card()
