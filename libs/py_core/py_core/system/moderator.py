import asyncio
from dataclasses import dataclass

from nanoid import generate

from py_core.system.model import ChildCardRecommendationResult, DialogueMessage, DialogueRole, CardInfo, \
    CardIdentity, \
    ParentGuideRecommendationResult, Dialogue, ParentGuideType, ParentExampleMessage, ParentGuideElement
from py_core.system.storage import SessionStorage
from py_core.system.task import ChildCardRecommendationGenerator
from py_core.system.task.parent_guide_recommendation import ParentGuideRecommendationGenerator, \
    ParentExampleMessageGenerator
from py_core.system.task.parent_guide_recommendation.dialogue_inspector import DialogueInspector
from py_core.utils.deepl_translator import DeepLTranslator
from py_core.utils.models import AsyncTaskInfo


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


@dataclass
class ParentExampleGenerationTaskSet:
    recommendation_id: str
    tasks: dict[str, AsyncTaskInfo | None]


class ModeratorSession:

    def __init__(self, storage: SessionStorage):
        self.__storage = storage

        self.__child_card_recommender = ChildCardRecommendationGenerator()
        self.__parent_guide_recommender = ParentGuideRecommendationGenerator()

        self.__next_speaker: DialogueRole = DialogueRole.Parent

        self.__deepl_translator = DeepLTranslator()

        self.__dialogue_inspector = DialogueInspector()
        self.__dialogue_inspection_task_info: AsyncTaskInfo | None = None

        self.__parent_example_generation_tasks: ParentExampleGenerationTaskSet | None = None

        self.__parent_example_generator = ParentExampleMessageGenerator()

    @property
    def next_speaker(self) -> DialogueRole:
        return self.__next_speaker

    def __clear_parent_example_generation_tasks(self):
        if self.__parent_example_generation_tasks is not None:
            for k, t in self.__parent_example_generation_tasks.tasks.items():
                if not t.task.done():
                    t.task.cancel()
            self.__parent_example_generation_tasks = None

    async def __parent_example_generate_func(self, dialogue: Dialogue, guide: ParentGuideElement, recommendation_id: str) -> ParentExampleMessage:
        message = await self.__parent_example_generator.generate(dialogue, guide, recommendation_id)
        await self.__storage.add_parent_example_message(message)
        return message

    def __place_parent_example_generation_tasks(self, dialogue: Dialogue, recommendation: ParentGuideRecommendationResult):
        self.__parent_example_generation_tasks = ParentExampleGenerationTaskSet(
            recommendation_id=recommendation.id,
            tasks={guide.id: AsyncTaskInfo(
                task_id=guide.id,
                task=asyncio.create_task(self.__parent_example_generate_func(dialogue, guide, recommendation.id))
            ) for guide in recommendation.guides if guide.type == ParentGuideType.Messaging}
        )

    @speaker(DialogueRole.Parent)
    async def submit_parent_message(self, parent_message: str,
                                    current_parent_guide: ParentGuideRecommendationResult | None = None) -> ChildCardRecommendationResult:

        try:
            # Clear if there is a pending example generation task.
            self.__clear_parent_example_generation_tasks()

            print("Translate parent message..")
            message_eng = await self.__deepl_translator.translate(
                text=parent_message,
                source_lang="KO", target_lang="EN-US",
                context="The message is from a parent to their child."
            )

            print("Translated parent message.")

            new_message = DialogueMessage(role=DialogueRole.Parent,
                                          content_localized=parent_message,
                                          content=message_eng,
                                          recommendation_id=current_parent_guide.id if current_parent_guide is not None else None)

            await self.__storage.add_dialogue_message(new_message)

            dialogue = await self.__storage.get_dialogue()

            # Start a background task for inspection.
            if self.__dialogue_inspection_task_info is not None:
                self.__dialogue_inspection_task_info.task.cancel()

            inspection_task_id = generate(size=5)

            self.__dialogue_inspection_task_info = AsyncTaskInfo(task_id=inspection_task_id,
                                                                 task=asyncio.create_task(
                                                                     self.__dialogue_inspector.inspect(dialogue,
                                                                                                       inspection_task_id)))

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

            # Join a dialogue inspection task
            dialogue_inspection_result = None
            if self.__dialogue_inspection_task_info is not None:
                dialogue_inspection_result, task_id = await self.__dialogue_inspection_task_info.task
                if task_id != self.__dialogue_inspection_task_info.task_id:
                    dialogue_inspection_result = None

            # Clear
            self.__dialogue_inspection_task_info = None

            recommendation = await self.__parent_guide_recommender.generate(dialogue, dialogue_inspection_result)

            await self.__storage.add_parent_guide_recommendation_result(recommendation)

            # Invoke an example generation task in advance.
            self.__clear_parent_example_generation_tasks()
            self.__place_parent_example_generation_tasks(dialogue, recommendation)

            self.__next_speaker = DialogueRole.Parent

            return recommendation

        except Exception as e:
            raise e

    @speaker(DialogueRole.Parent)
    async def request_parent_example_message(self, recommendation_id: str, guide_id: str) -> ParentExampleMessage:
        if (self.__parent_example_generation_tasks is not None
                and self.__parent_example_generation_tasks.recommendation_id == recommendation_id):
            example_message: ParentExampleMessage = await self.__parent_example_generation_tasks.tasks[guide_id].task
            return example_message
        else:
            example_message: ParentExampleMessage = await self.__storage.get_parent_example_message(recommendation_id,
                                                                                                    guide_id)
            if example_message is not None:
                return example_message
            else:
                dialogue = await self.__storage.get_dialogue()
                recommendation = await self.__storage.get_parent_guide_recommendation_result(recommendation_id)
                guide = [guide for guide in recommendation.guides if guide.id == guide_id][0]
                example_message: ParentExampleMessage = await self.__parent_example_generate_func(dialogue, guide, recommendation.id)
                return example_message

