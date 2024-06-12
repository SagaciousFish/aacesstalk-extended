from abc import ABC, abstractmethod
from typing import Optional

from py_core.system.model import ChildCardRecommendationResult, Dialogue, DialogueMessage, \
    ParentGuideRecommendationResult, id_generator, ParentExampleMessage, InterimCardSelection, SessionInfo, Interaction, DialogueTurn
from py_core.system.session_topic import SessionTopicInfo


class SessionStorage(ABC):

    def __init__(self, session_id: str):
        self.__session_id = session_id

    @classmethod
    @abstractmethod
    async def _load_session_info(cls, session_id: str) -> SessionInfo | None:
        pass
    @classmethod
    async def restore_instance(cls, id: str)->Optional['SessionStorage']:
        session_info = await cls._load_session_info(id)
        if session_info is not None:
            return cls(session_id=session_info.id)
        else:
            return None

    @property
    def session_id(self) -> str:
        return self.__session_id

    async def get_session_info(self) -> SessionInfo:
        return await self._load_session_info(self.session_id)

    @abstractmethod
    async def update_session_info(self, info: SessionInfo):
        pass

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
    async def get_latest_card_selection(self, turn_id: str | None = None) -> InterimCardSelection | None:
        pass

    @abstractmethod
    async def add_card_selection(self, selection: InterimCardSelection):
        pass

    @abstractmethod
    async def get_latest_parent_guide_recommendation(self, turn_id: str | None = None) -> ParentGuideRecommendationResult | None:
        pass

    @abstractmethod
    async def get_latest_child_card_recommendation(self, turn_id: str | None = None) -> ChildCardRecommendationResult | None:
        pass

    @abstractmethod
    async def get_latest_dialogue_message(self) -> DialogueMessage | None:
        pass

    @abstractmethod
    async def delete_entities(self):
        pass

    @abstractmethod
    async def upsert_dialogue_turn(self, turn: DialogueTurn):
        pass

    @abstractmethod
    async def get_latest_turn(self) -> DialogueTurn | None:
        pass

    @abstractmethod
    async def add_interaction(self, interaction: Interaction):
        pass
