from abc import ABC, abstractmethod

from py_core.system.model import ChildCardRecommendationResult, Dialogue, DialogueMessage, \
    ParentGuideRecommendationResult, id_generator, ParentExampleMessage, InterimCardSelection


class SessionStorage(ABC):

    def __init__(self, session_id: str | None = None):
        self.__session_id = session_id or id_generator()

    @property
    def session_id(self) -> str:
        return self.__session_id

    @abstractmethod
    async def add_dialogue_message(self, message: DialogueMessage):
        pass

    @abstractmethod
    async def get_dialogue(self) -> Dialogue:
        pass

    @abstractmethod
    async def add_card_recommendation_result(self, result: ChildCardRecommendationResult):
        pass

    @abstractmethod
    async def add_parent_guide_recommendation_result(self, result: ParentGuideRecommendationResult):
        pass

    @abstractmethod
    async def add_parent_example_message(self, message: ParentExampleMessage):
        pass

    @abstractmethod
    async def get_card_recommendation_result(self, recommendation_id: str) -> ChildCardRecommendationResult | None:
        pass

    @abstractmethod
    async def get_parent_guide_recommendation_result(self,
                                                     recommendation_id: str) -> ParentGuideRecommendationResult | None:
        pass

    @abstractmethod
    async def get_parent_example_message(self, recommendation_id: str, guide_id: str) -> ParentExampleMessage | None:
        pass

    @abstractmethod
    async def get_latest_card_selection(self) -> InterimCardSelection | None:
        pass

    @abstractmethod
    async def add_card_selection(self, selection: InterimCardSelection):
        pass

    @abstractmethod
    async def get_latest_parent_guide_recommendation(self) -> ParentGuideRecommendationResult | None:
        pass

    @abstractmethod
    async def get_latest_child_card_recommendation(self) -> ChildCardRecommendationResult | None:
        pass

    @abstractmethod
    async def get_latest_dialogue_message(self) -> DialogueMessage | None:
        pass
