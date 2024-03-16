from functools import cached_property

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from os import path, getcwd, makedirs

from py_core.system.model import ParentGuideRecommendationResult, ChildCardRecommendationResult, Dialogue, \
    DialogueMessage, DialogueTypeAdapter
from py_core.system.storage import SessionStorage


class SessionJsonStorage(SessionStorage):
    TABLE_MESSAGES = "messages"
    TABLE_CARD_RECOMMENDATIONS = "card_recommendations"
    TABLE_PARENT_RECOMMENDATIONS = "parent_recommendations"

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

    async def add_dialogue_message(self, message: DialogueMessage):
        table = self.db.table(self.TABLE_MESSAGES)
        table.insert(message.model_dump())

    async def get_dialogue(self) -> Dialogue:
        table = self.db.table(self.TABLE_MESSAGES)
        data = table.all()
        converted = DialogueTypeAdapter.validate_python(data)
        converted.sort(key=lambda m: m.timestamp)
        return converted

    async def add_card_recommendation_result(self, result: ChildCardRecommendationResult):
        table = self.db.table(self.TABLE_CARD_RECOMMENDATIONS)
        table.insert(result.model_dump())

    async def add_parent_guide_recommendation_result(self, result: ParentGuideRecommendationResult):
        table = self.db.table(self.TABLE_PARENT_RECOMMENDATIONS)
        table.insert(result.model_dump())

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
