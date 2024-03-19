from libs.py_core.py_core.system.model import ParentGuideRecommendationResult, ChildCardRecommendationResult, Dialogue, \
    DialogueMessage
from libs.py_core.py_core.system.storage import SessionStorage


class SQLSessionStorage(SessionStorage):
    def __init__(self, session_id: str | None = None):
        super().__init__(session_id)


    async def add_dialogue_message(self, message: DialogueMessage):
        pass

    async def get_dialogue(self) -> Dialogue:
        pass

    async def add_card_recommendation_result(self, result: ChildCardRecommendationResult):
        pass

    async def add_parent_guide_recommendation_result(self, result: ParentGuideRecommendationResult):
        pass

    async def get_card_recommendation_result(self, recommendation_id: str) -> ChildCardRecommendationResult | None:
        pass

    async def get_parent_guide_recommendation_result(self,
                                                     recommendation_id: str) -> ParentGuideRecommendationResult | None:
        pass
