from py_core.system.model import Dialogue, DialogueTurn, Interaction, ParentGuideRecommendationResult, ChildCardRecommendationResult, \
    DialogueMessage, ParentExampleMessage, InterimCardSelection, DialogueRole, ModelWithIdAndTimestamp, SessionInfo
from py_core.system.storage.session.session_storage import SessionStorage


class OnMemorySessionStorage(SessionStorage):

    __session_infos: dict[str, SessionInfo] = {}

    def __init__(self, id: str):
        super().__init__(id)

        self.__dialogue: Dialogue = []
        self.__parent_guide_recommendations: dict[str, ParentGuideRecommendationResult] = {}
        self.__card_recommendations: dict[str, ChildCardRecommendationResult] = {}

        self.__parent_example_messages: dict[tuple[str, str], ParentExampleMessage] = {}

        self.__interim_card_selections: dict[str, InterimCardSelection] = {}

        self.__turns: dict[str, DialogueTurn] = {}

        self.__interactions: dict[str, Interaction] = {}



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

    async def add_parent_example_message(self, message: ParentExampleMessage):
        self.__parent_example_messages[(message.recommendation_id, message.guide_id)] = message

    async def get_parent_example_message(self, recommendation_id: str, guide_id: str) -> ParentExampleMessage | None:
        if (recommendation_id, guide_id) in self.__parent_example_messages:
            return self.__parent_example_messages[(recommendation_id, guide_id)]
        else:
            return None

    async def __get_latest_model(self, model_dict: dict[str, ModelWithIdAndTimestamp], timestamp_column: str = "timestamp") -> ModelWithIdAndTimestamp | None:
        sorted_selections = sorted(
            [v for k, v in model_dict.items()],
            key=lambda s: s[timestamp_column], reverse=True)
        if len(sorted_selections) > 0:
            return sorted_selections[0]
        else:
            return None

    async def get_latest_card_selection(self) -> InterimCardSelection | None:
        return await self.__get_latest_model(self.__interim_card_selections)

    async def add_card_selection(self, selection: InterimCardSelection):
        self.__interim_card_selections[selection.id] = selection

    async def get_latest_parent_guide_recommendation(self) -> ParentGuideRecommendationResult | None:
        return await self.__get_latest_model(self.__parent_guide_recommendations)

    async def get_latest_child_card_recommendation(self) -> ChildCardRecommendationResult | None:
        return await self.__get_latest_model(self.__card_recommendations)

    async def get_latest_dialogue_message(self) -> DialogueMessage | None:
        if len(self.__dialogue) == 0:
            return None
        else:
            return self.__dialogue[len(self.__dialogue) - 1]

    async def delete_entities(self):
        self.__dialogue = []
        self.__parent_guide_recommendations = {}
        self.__card_recommendations = {}
        self.__parent_example_messages = {}
        self.__interim_card_selections = {}
        self.__interactions = {}
        self.__turns = {}

    async def upsert_dialogue_turn(self, turn: DialogueTurn):
        self.__turns[turn.id] = turn

    async def add_interaction(self, interaction: Interaction):
        self.__interactions[interaction.id] = interaction

    async def get_latest_turn(self) -> DialogueTurn | None:
        return await self.__get_latest_model(self.__turns)

    @classmethod
    async def _load_session_info(cls, session_id: str) -> SessionInfo | None:
        return cls.__session_infos[session_id] if session_id in cls.__session_infos else None

    async def update_session_info(self, info: SessionInfo):
        self.__session_infos[info.id] = info




