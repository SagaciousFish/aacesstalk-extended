from asyncio.threads import to_thread
from enum import StrEnum
from os import path

from pydantic import BaseModel, Field, validate_call

from py_core.system.model import CardInfo, ChildGender, ParentType, id_generator
from py_core.system.storage import UserStorage
from py_core.system.task.card_image_matching.card_image_db_retriever import CardImageDBRetriever

from py_core.utils.default_cards import find_default_card, find_default_card_by_id
from py_core.utils.models import CardImageInfo
from py_core.config import AACessTalkConfig


class CardType(StrEnum):
    stock = "stock"
    custom = "custom"
    static = "static"


class CardImageMatching(BaseModel):
    id: str = Field(default_factory=id_generator)
    card_info_id: str
    type: CardType
    image_id: str


class CardImageMatcher:

    is_class_vars_initialized = False

    @classmethod
    def _init_class_vars(cls):
        if not cls.is_class_vars_initialized:
            # Initialize
            cls.__db_retriever = CardImageDBRetriever()

            cls.is_class_vars_initialized = True


    def __init__(self, user_storage: UserStorage):
        self.__user_storage = user_storage
        self._init_class_vars()

    async def match_card_images(self, card_info_list: list[CardInfo], parent_type: ParentType, child_gender: ChildGender) -> list[CardImageMatching]:

        result = [None] * len(card_info_list)

        # Look up user defined cards first
        for i, card_info in enumerate(card_info_list):
            custom_card_query_result = await self.__user_storage.query_user_defined_card(card_info.category, card_info.label_localized)
            if custom_card_query_result is not None:
                result[i] = CardImageMatching(card_info_id=card_info.id, type=CardType.custom, image_id=custom_card_query_result.id)
        
        # Look up default cards
        for i, card_info in enumerate(card_info_list):
            if result[i] is None:
                default_card = find_default_card(card_info.label_localized, card_info.category, parent_type)
                print(f"Default card for {card_info.category}, {card_info.label_localized}: {default_card}")
                if default_card is not None:
                    image_filename = default_card.get_image_path_for_dyad(parent_type=parent_type, child_gender=child_gender)
                    if image_filename is not None:
                        result[i] = CardImageMatching(card_info_id=card_info.id, type=CardType.static, image_id=default_card.id)
                        

        # Lookup vector db

        idx_to_retrive = [i for i, c in enumerate(card_info_list) if result[i] is None]

        db_card_image_infos: list[list[CardImageInfo]] = await self.__db_retriever.query_nearest_card_image_infos([c for i, c in enumerate(card_info_list) if result[i] is None])
        for i, cards in enumerate(db_card_image_infos):
            result[idx_to_retrive[i]] = CardImageMatching(card_info_id=card_info_list[idx_to_retrive[i]].id, type=CardType.stock, image_id=cards[0].id)
        
        return result

    @validate_call
    async def get_card_image_filepath(self, type: CardType, image_id: str, parent_type: ParentType, child_gender: ChildGender)->str:
        if type is CardType.custom:
            info = await self.__user_storage.get_user_defined_card(image_id)
            return path.join(self.__user_storage.get_user_custom_card_dir_path(), info.image_filename)
        elif type is CardType.stock:
            return path.join(AACessTalkConfig.card_image_directory_path, self.__db_retriever.get_card_image_info(image_id).filename)
        elif type is CardType.static:
            return path.join(AACessTalkConfig.card_image_directory_path, find_default_card_by_id(image_id).get_image_path_for_dyad(parent_type, child_gender))