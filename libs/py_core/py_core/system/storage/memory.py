from py_core.system.model import Dialogue, ParentGuideRecommendationResult, ChildCardRecommendationResult, \
    DialogueMessage
from py_core.system.storage.session_storage import SessionStorage


class SessionMemoryStorage(SessionStorage):


    def __init__(self, session_id: str | None = None):
        super().__init__(session_id)

        self.__dialogue: Dialogue = []
        self.__parent_guide_recommendations: dict[str, ParentGuideRecommendationResult] = {}
        self.__card_recommendations: dict[str, ChildCardRecommendationResult] = {}

    async def add_dialogue_message(self, message: DialogueMessage):
        self.__dialogue.append(message)

    async def get_dialogue(self) -> Dialogue:
        return self.__dialogue

    async def add_card_recommendation_result(self, result: ChildCardRecommendationResult):
        self.__card_recommendations[result.id] = result

    async def add_parent_guide_recommendation_result(self, result: ParentGuideRecommendationResult):
        self.__parent_guide_recommendations[result.id] = result

    async def get_card_recommendation_result(self, recommendation_id: str) -> ChildCardRecommendationResult | None:
        if recommendation_id in self.__card_recommendations:
            return self.__card_recommendations[recommendation_id]
        else:
            return None

    async def get_parent_guide_recommendation_result(self,
                                                     recommendation_id: str) -> ParentGuideRecommendationResult | None:
        if recommendation_id in self.__parent_guide_recommendations:
            return self.__parent_guide_recommendations[recommendation_id]
        else:
            return None
