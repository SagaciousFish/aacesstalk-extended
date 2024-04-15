import asyncio
from asyncio import to_thread

import deepl
from deepl import TextResult
from chatlib.utils.env_helper import get_env_variable

from py_core.system.model import ChildCardRecommendationResult, Dialogue, DialogueMessage, DialogueRole, CardInfo, \
    CardIdentity, \
    ParentGuideRecommendationResult
from py_core.system.storage import SessionStorage
from py_core.system.task import ChildCardRecommendationGenerator
from py_core.system.task.parent_guide_recommendation import ParentGuideRecommendationGenerator
from py_core.utils.deepl_translator import DeepLTranslator


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

        self.__deepl_translator = DeepLTranslator()

    @property
    def next_speaker(self) -> DialogueRole:
        return self.__next_speaker

    @speaker(DialogueRole.Parent)
    async def submit_parent_message(self, parent_message: str,
                                    current_parent_guide: ParentGuideRecommendationResult | None = None) -> ChildCardRecommendationResult:

        try:
            message_eng = await self.__deepl_translator.translate(
                text=parent_message,
                source_lang="KO", target_lang="EN-US",
                context="The message is from a parent to their child."
            )

            new_message = DialogueMessage(role=DialogueRole.Parent,
                                          content=parent_message,
                                          content_en=message_eng,
                                          recommendation_id=current_parent_guide.id if current_parent_guide is not None else None)

            await self.__storage.add_dialogue_message(new_message)

            dialogue = await self.__storage.get_dialogue()

            recommendation = await self.__child_card_recommender.generate(dialogue, None, None)

            await self.__storage.add_card_recommendation_result(recommendation)

            self.__next_speaker = DialogueRole.Child

            return recommendation
        except Exception as e:
            raise e


    async def __get_card_info_from_identities(self, cards: list[CardIdentity] | list[CardInfo]) -> list[CardInfo]:
        cards = [card_identity if isinstance(card_identity, CardInfo) else (
            await self.__storage.get_card_recommendation_result(card_identity.recommendation_id)).find_card_by_id(
            card_identity.id) for card_identity in cards]
        return [c for c in cards if c is not None]

    @speaker(DialogueRole.Child)
    async def refresh_child_card_recommendation(self, interim_cards: list[CardIdentity] | list[CardInfo],
                                                prev_recommendation: ChildCardRecommendationResult) -> ChildCardRecommendationResult:
        try:
            dialogue = await self.__storage.get_dialogue()
            interim_cards = await self.__get_card_info_from_identities(interim_cards)

            recommendation = await self.__child_card_recommender.generate(dialogue, interim_cards, prev_recommendation)

            await self.__storage.add_card_recommendation_result(recommendation)

            return recommendation
        except Exception as e:
            raise e

    @speaker(DialogueRole.Child)
    async def submit_child_selected_card(self, selected_cards: list[CardIdentity] | list[CardInfo]) -> ParentGuideRecommendationResult:
        try:
            selected_cards = await self.__get_card_info_from_identities(selected_cards)
            await self.__storage.add_dialogue_message(DialogueMessage(
                role=DialogueRole.Child,
                content=selected_cards
            ))

            dialogue = await self.__storage.get_dialogue()

            recommendation = await self.__parent_guide_recommender.generate(dialogue)

            await self.__storage.add_parent_guide_recommendation_result(recommendation)

            self.__next_speaker = DialogueRole.Parent

            return recommendation

        except Exception as e:
            raise e
