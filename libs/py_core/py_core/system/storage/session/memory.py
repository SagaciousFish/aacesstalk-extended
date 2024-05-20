from py_core.system.model import Dialogue, ParentGuideRecommendationResult, ChildCardRecommendationResult, \
    DialogueMessage, ParentExampleMessage, InterimCardSelection, DialogueRole, ModelWithIdAndTimestamp
from py_core.system.storage.session.session_storage import SessionStorage


class OnMemorySessionStorage(SessionStorage):

    def __init__(self, session_id: str | None = None):
        super().__init__(session_id)

        self.__dialogue: Dialogue = []
        self.__parent_guide_recommendations: dict[str, ParentGuideRecommendationResult] = {}
        self.__card_recommendations: dict[str, ChildCardRecommendationResult] = {}

        self.__parent_example_messages: dict[tuple[str, str], ParentExampleMessage] = {}

        self.__interim_card_selections: dict[str, InterimCardSelection] = {}

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

    async def __get_latest_model(self, model_dict: [str, ModelWithIdAndTimestamp], latest_role: DialogueRole) -> ModelWithIdAndTimestamp | None:
        latest_message = await self.get_latest_dialogue_message()
        if latest_message is not None and latest_message.role == latest_role:
            sorted_selections = sorted(
                [v for k, v in model_dict.items() if v.timestamp > latest_message.timestamp],
                key=lambda s: s.timestamp, reverse=True)
            if len(sorted_selections) > 0:
                return sorted_selections[0]
            else:
                return None
        else:
            return None

    async def get_latest_card_selection(self) -> InterimCardSelection | None:
        return await self.__get_latest_model(self.__interim_card_selections, latest_role=DialogueRole.Parent)

    async def add_card_selection(self, selection: InterimCardSelection):
        self.__interim_card_selections[selection.id] = selection

    async def get_latest_parent_guide_recommendation(self) -> ParentGuideRecommendationResult | None:
        return await self.__get_latest_model(self.__parent_guide_recommendations, latest_role=DialogueRole.Child)

    async def get_latest_child_card_recommendation(self) -> ChildCardRecommendationResult | None:
        return await self.__get_latest_model(self.__card_recommendations, latest_role=DialogueRole.Parent)

    async def get_latest_dialogue_message(self) -> DialogueMessage | None:
        if len(self.__dialogue) == 0:
            return None
        else:
            return self.__dialogue[len(self.__dialogue) - 1]
