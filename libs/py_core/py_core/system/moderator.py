import asyncio
from dataclasses import dataclass
from enum import StrEnum

from nanoid import generate

from py_core.system.model import ChildCardRecommendationResult, DialogueMessage, DialogueRole, CardInfo, \
    CardIdentity, \
    ParentGuideRecommendationResult, Dialogue, ParentGuideType, ParentExampleMessage, ParentGuideElement, \
    InterimCardSelection, Dyad
from py_core.system.session_topic import SessionTopicInfo
from py_core.system.storage import SessionStorage
from py_core.system.task import ChildCardRecommendationGenerator
from py_core.system.task.parent_guide_recommendation import ParentGuideRecommendationGenerator, \
    ParentExampleMessageGenerator
from py_core.system.task.parent_guide_recommendation.dialogue_inspector import DialogueInspector
from py_core.utils.deepl_translator import DeepLTranslator
from py_core.utils.models import AsyncTaskInfo
from chatlib.llm.integration import GPTChatCompletionAPI

from py_core.utils.vector_db import VectorDB


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

    class_variables_initialized = False

    @classmethod
    def __init_class_vars(cls):
        if cls.class_variables_initialized is False:
            print("Initialize Moderator session class variables..")
            vector_db = VectorDB()
            cls.__child_card_recommender = ChildCardRecommendationGenerator(vector_db)
            cls.__parent_guide_recommender = ParentGuideRecommendationGenerator()

            cls.__deepl_translator = DeepLTranslator()

            cls.__dialogue_inspector = DialogueInspector()
            cls.__parent_example_generator = ParentExampleMessageGenerator(vector_db)
            cls.class_variables_initialized = True

    def __init__(self, dyad: Dyad, storage: SessionStorage):

        self.__init_class_vars()

        self.__storage = storage

        self.__dyad = dyad

        self.__next_speaker: DialogueRole = DialogueRole.Parent

        self.__dialogue_inspection_task_info: AsyncTaskInfo | None = None

        self.__parent_example_generation_tasks: ParentExampleGenerationTaskSet | None = None


    @property
    def storage(self) -> SessionStorage:
        return self.__storage

    @storage.setter
    def storage(self, storage: SessionStorage):
        self.__storage = storage

    @classmethod
    def assert_authorize(cls):
        GPTChatCompletionAPI.assert_authorize()
        DeepLTranslator.assert_authorize()


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

    async def generate_parent_guide_recommendation(self) -> ParentGuideRecommendationResult:
        dialogue = await self.__storage.get_dialogue()

        # Join a dialogue inspection task
        dialogue_inspection_result = None
        if self.__dialogue_inspection_task_info is not None:
            dialogue_inspection_result, task_id = await self.__dialogue_inspection_task_info.task
            if task_id != self.__dialogue_inspection_task_info.task_id:
                dialogue_inspection_result = None

        # Clear
        self.__dialogue_inspection_task_info = None

        recommendation = await self.__parent_guide_recommender.generate(self.__dyad.parent_type, self.storage.session_topic, dialogue, dialogue_inspection_result)

        await self.__storage.add_parent_guide_recommendation_result(recommendation)

        # Invoke an example generation task in advance.
        self.__clear_parent_example_generation_tasks()
        self.__place_parent_example_generation_tasks(dialogue, recommendation)

        return recommendation

    @speaker(DialogueRole.Parent)
    async def submit_parent_message(self, parent_message: str) -> ChildCardRecommendationResult:

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

            current_guide = await self.storage.get_latest_parent_guide_recommendation()
            if current_guide is None:
                # Load Initial guide
                pass

            new_message = DialogueMessage(role=DialogueRole.Parent,
                                          content_localized=parent_message,
                                          content=message_eng,
                                          recommendation_id=current_guide.id if current_guide is not None else None)

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

            recommendation = await self.__child_card_recommender.generate(topic_info=self.storage.session_topic, 
                                                                          parent_type=self.__dyad.parent_type,
                                                                          dialogue=dialogue, interim_cards=None, previous_recommendation=None)

            await self.__storage.add_card_recommendation_result(recommendation)

            self.__next_speaker = DialogueRole.Child

            return recommendation
        except Exception as e:
            raise e

    async def get_card_info_from_identities(self, cards: list[CardIdentity] | list[CardInfo]) -> list[CardInfo]:
        cards = [card_identity if isinstance(card_identity, CardInfo) else (
            await self.__storage.get_card_recommendation_result(card_identity.recommendation_id)).find_card_by_id(
            card_identity.id) for card_identity in cards]
        return [c for c in cards if c is not None]

    @speaker(DialogueRole.Child)
    async def refresh_child_card_recommendation(self) -> ChildCardRecommendationResult:
        try:
            dialogue = await self.__storage.get_dialogue()

            interim_card_selection = await self.storage.get_latest_card_selection()
            prev_recommendation = await self.storage.get_latest_child_card_recommendation()

            interim_cards = await self.get_card_info_from_identities(interim_card_selection.cards)

            recommendation = await self.__child_card_recommender.generate(self.__dyad.parent_type, self.storage.session_topic, dialogue, interim_cards, prev_recommendation)

            await self.__storage.add_card_recommendation_result(recommendation)

            return recommendation
        except Exception as e:
            raise e

    @speaker(DialogueRole.Child)
    async def select_child_card(self, card_identity: CardIdentity) -> InterimCardSelection:
        try:
            current_card_selection = await self.storage.get_latest_card_selection()
            new_card_selection = InterimCardSelection(cards=[*current_card_selection.cards, card_identity] if current_card_selection is not None else [card_identity])
            await self.storage.add_card_selection(new_card_selection)
            return new_card_selection
        except Exception as e:
            raise e

    @speaker(DialogueRole.Child)
    async def confirm_child_card_selection(self) -> ParentGuideRecommendationResult:
        try:
            interim_card_selection = await self.storage.get_latest_card_selection()
            if interim_card_selection is not None:
                selected_cards = await self.get_card_info_from_identities(interim_card_selection.cards)
                await self.__storage.add_dialogue_message(DialogueMessage(
                    role=DialogueRole.Child,
                    content=selected_cards
                ))

                parent_recommendation = await self.generate_parent_guide_recommendation()

                self.__next_speaker = DialogueRole.Parent

                return parent_recommendation
            else:
                raise ValueError("No interim card selection.")

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

