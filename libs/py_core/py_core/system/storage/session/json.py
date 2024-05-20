from functools import cached_property

from pydantic import BaseModel
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from os import path, getcwd, makedirs

from py_core.system.model import ParentGuideRecommendationResult, ChildCardRecommendationResult, Dialogue, \
    DialogueMessage, DialogueTypeAdapter, ParentExampleMessage, InterimCardSelection, DialogueRole, CardCategory, \
    UserCustomCardImageInfo
from py_core.system.storage import SessionStorage


class JsonSessionStorage(SessionStorage):


    TABLE_MESSAGES = "messages"
    TABLE_CARD_RECOMMENDATIONS = "card_recommendations"
    TABLE_PARENT_RECOMMENDATIONS = "parent_recommendations"
    TABLE_PARENT_EXAMPLE_MESSAGES = "parent_example_messages"
    TABLE_CARD_SELECTIONS = "card_selections"
    TABLE_CUSTOM_CARD_IMAGES = "custom_care_images"

    def __init__(self, session_id: str | None = None):
        super().__init__(session_id)

    @property
    def session_db_path(self) -> str:
        dir_path = path.join(getcwd(), "../../database/json/sessions", self.session_id)
        if not path.exists(dir_path):
            makedirs(dir_path)

        return path.join(dir_path, "db.json")

    @cached_property
    def db(self) -> TinyDB:
        return TinyDB(self.session_db_path, CachingMiddleware(JSONStorage))

    def __insert_one(self, table_name: str, model: BaseModel):
        table = self.db.table(table_name)
        table.insert(model.model_dump())

    async def add_dialogue_message(self, message: DialogueMessage):
        self.__insert_one(self.TABLE_MESSAGES, message)

    async def get_dialogue(self) -> Dialogue:
        table = self.db.table(self.TABLE_MESSAGES)
        data = table.all()
        converted = DialogueTypeAdapter.validate_python(data)
        converted.sort(key=lambda m: m.timestamp)
        return converted

    async def add_card_recommendation_result(self, result: ChildCardRecommendationResult):
        self.__insert_one(self.TABLE_CARD_RECOMMENDATIONS, result)

    async def add_parent_guide_recommendation_result(self, result: ParentGuideRecommendationResult):
        self.__insert_one(self.TABLE_PARENT_RECOMMENDATIONS, result)

    async def get_card_recommendation_result(self, recommendation_id: str) -> ChildCardRecommendationResult | None:
        table = self.db.table(self.TABLE_CARD_RECOMMENDATIONS)
        q = Query()
        result = table.search(q.id == recommendation_id)
        if len(result) > 0:
            return ChildCardRecommendationResult(**result[0])
        else:
            return None

    async def get_parent_guide_recommendation_result(self,
                                                     recommendation_id: str) -> ParentGuideRecommendationResult | None:
        table = self.db.table(self.TABLE_PARENT_RECOMMENDATIONS)
        q = Query()
        result = table.search(q.id == recommendation_id)
        if len(result) > 0:
            return ParentGuideRecommendationResult(**result[0])
        else:
            return None

    async def add_parent_example_message(self, message: ParentExampleMessage):
        self.__insert_one(self.TABLE_PARENT_EXAMPLE_MESSAGES, message)

    async def get_parent_example_message(self, recommendation_id: str, guide_id: str) -> ParentExampleMessage | None:
        table = self.db.table(self.TABLE_PARENT_EXAMPLE_MESSAGES)
        q = Query()
        result = table.search((q.recommendation_id == recommendation_id) & (q.guide_id == guide_id))
        if len(result) > 0:
            return ParentExampleMessage(**result[0])
        else:
            return None

    async def __get_latest_model(self, table_name: str, latest_role: DialogueRole) -> dict | None:
        latest_message = await self.get_latest_dialogue_message()
        if latest_message is not None and latest_message.role == latest_role:
            table = self.db.table(table_name)
            sorted_selections = sorted(
                [row for row in table.all() if row["timestamp"] > latest_message.timestamp],
                key=lambda s: s["timestamp"], reverse=True)
            if len(sorted_selections) > 0:
                return sorted_selections[0]
            else:
                return None
        else:
            return None

    async def get_latest_card_selection(self) -> InterimCardSelection | None:
        d = await self.__get_latest_model(self.TABLE_CARD_SELECTIONS, latest_role=DialogueRole.Parent)
        return InterimCardSelection(**d) if d is not None else None

    async def add_card_selection(self, selection: InterimCardSelection):
        self.__insert_one(self.TABLE_CARD_SELECTIONS, selection)

    async def get_latest_parent_guide_recommendation(self) -> ParentGuideRecommendationResult | None:
        d = await self.__get_latest_model(self.TABLE_PARENT_RECOMMENDATIONS, latest_role=DialogueRole.Child)
        return ParentGuideRecommendationResult(**d) if d is not None else None

    async def get_latest_child_card_recommendation(self) -> ChildCardRecommendationResult | None:
        d = await self.__get_latest_model(self.TABLE_CARD_RECOMMENDATIONS, latest_role=DialogueRole.Parent)
        return ChildCardRecommendationResult(**d) if d is not None else None

    async def get_latest_dialogue_message(self) -> DialogueMessage | None:
        table = self.db.table(self.TABLE_MESSAGES)
        result = sorted(table.all(), key=lambda m: m["timestamp"], reverse=True)
        if len(result) > 0:
            return DialogueMessage(**result[0])
        else:
            return None

    async def add_custom_card(self, info: UserCustomCardImageInfo):
        self.__insert_one(self.TABLE_CUSTOM_CARD_IMAGES, info)

    async def query_custom_card(self, category: CardCategory, label_localized: str) -> UserCustomCardImageInfo | None:
        pass
