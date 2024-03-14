import asyncio

from py_core.system.model import ChildCardRecommendationResult, Dialogue, DialogueMessage, DialogueRole, CardInfo, \
    ParentGuideRecommendationResult
from py_core.system.storage import SessionStorage
from py_core.system.task import ChildCardRecommendationGenerator
from py_core.system.task.parent_guide_recommendation import ParentGuideRecommendationGenerator

def speaker(role: DialogueRole):
    def decorator(func):
        async def wrapper(self: 'ModeratorSession', *args, **kwargs):
            if self.next_speaker != role:
                raise Exception("Wrong speaker function called.")
            else:
                if asyncio.iscoroutinefunction(func):
                    return await func(self, *args, **kwargs)
                else:
                    return func(self, *args, **kwargs)
        return wrapper
    return decorator

class ModeratorSession:

    def __init__(self, storage: SessionStorage):
        self.__storage = storage

        self.__child_card_recommender = ChildCardRecommendationGenerator()
        self.__parent_guide_recommender = ParentGuideRecommendationGenerator()

        self.__next_speaker: DialogueRole = DialogueRole.Parent

    @property
    def next_speaker(self)->DialogueRole:
        return self.__next_speaker


    @speaker(DialogueRole.Parent)
    async def submit_parent_message(self, parent_message: str) -> ChildCardRecommendationResult:

        try:
            new_message = DialogueMessage(speaker=DialogueRole.Parent,
                                          content=parent_message)

            await self.__storage.add_dialogue_message(new_message)

            dialogue = await self.__storage.get_dialogue()

            recommendation = await self.__child_card_recommender.generate(dialogue, None, None)

            await self.__storage.add_card_recommendation_result(recommendation)


            self.__next_speaker = DialogueRole.Child

            return recommendation
        except Exception as e:
            raise e

    @speaker(DialogueRole.Child)
    async def refresh_child_card_recommendation(self, interim_cards: list[CardInfo],
                                                prev_recommendation: ChildCardRecommendationResult) -> ChildCardRecommendationResult:
        try:
            dialogue = await self.__storage.get_dialogue()
            recommendation = await self.__child_card_recommender.generate(dialogue, interim_cards, prev_recommendation)

            await self.__storage.add_card_recommendation_result(recommendation)

            return recommendation
        except Exception as e:
            raise e

    @speaker(DialogueRole.Child)
    async def submit_child_selected_card(self, selected_cards: list[CardInfo]) -> ParentGuideRecommendationResult:
        try:
            await self.__storage.add_dialogue_message(DialogueMessage(
                speaker=DialogueRole.Child,
                content=selected_cards
            ))

            dialogue = await self.__storage.get_dialogue()


            recommendation = await self.__parent_guide_recommender.generate(dialogue)

            await self.__storage.add_parent_guide_recommendation_result(recommendation)

            self.__next_speaker = DialogueRole.Parent

            return recommendation

        except Exception as e:
            raise e


