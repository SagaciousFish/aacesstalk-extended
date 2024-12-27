import asyncio
from dataclasses import dataclass
from typing import Optional

from nanoid import generate

from chatlib.utils.time import get_timestamp

from py_core.system.model import ChildCardRecommendationResult, DialogueMessage, DialogueRole, CardInfo, \
    CardIdentity, DialogueTurn, Interaction, InteractionType, \
    ParentGuideRecommendationResult, Dialogue, ParentGuideType, ParentExampleMessage, ParentGuideElement, \
    InterimCardSelection, Dyad, SessionInfo, SessionStatus, UserLocale
from py_core.system.session_topic import SessionTopicInfo
from py_core.system.storage import SessionStorage
from py_core.system.task import ChildCardRecommendationGenerator
from py_core.system.task.parent_guide_recommendation import ParentGuideRecommendationGenerator, \
    ParentExampleMessageGenerator
from py_core.system.task.parent_guide_recommendation.dialogue_inspector import DialogueInspector
from py_core.system.task.parent_guide_recommendation.static_guide_factory import StaticGuideFactory
from py_core.utils.deepl_translator import DeepLTranslator
from py_core.utils.models import AsyncTaskInfo
from chatlib.llm.integration import GPTChatCompletionAPI

from py_core.utils.speech import ClovaVoice, ClovaSpeech

from py_core.utils.speech.clova_speech_long import ClovaLongSpeech
from py_core.utils.vector_db import VectorDB

class WrongSessionStatusError(BaseException):
    pass

def speaker(role: DialogueRole):
    def decorator(func):
        async def wrapper(self: 'ModeratorSession', *args, **kwargs):
            if (await self.current_speaker()) != role:
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

            cls.__static_guide_factory = StaticGuideFactory()

            cls.class_variables_initialized = True

    def __init__(self, dyad: Dyad, storage: SessionStorage):

        self.__init_class_vars()

        self.__storage = storage

        self.__dyad = dyad

        self.__dialogue_inspection_task_info: AsyncTaskInfo | None = None

        self.__parent_example_generation_tasks: ParentExampleGenerationTaskSet | None = None


    @property
    def storage(self) -> SessionStorage:
        return self.__storage
    
    @property
    def dyad(self) -> Dyad:
        return self.__dyad
    
    @property
    def locale(self) -> UserLocale:
        return self.__dyad.locale

    @storage.setter
    def storage(self, storage: SessionStorage):
        self.__storage = storage

    async def session_topic(self)->SessionTopicInfo:
        info = await self.storage.get_session_info()
        return info.topic

    async def get_session_status(self) -> SessionStatus:
        info = await self.storage.get_session_info()
        return info.status


    @classmethod
    def assert_authorize(cls):
        GPTChatCompletionAPI.assert_authorize()
        DeepLTranslator.assert_authorize()
        ClovaVoice.assert_authorize()
        #ClovaSpeech.assert_authorize()
        ClovaLongSpeech.assert_authorize()

    @classmethod
    async def create(cls, dyad: Dyad, topic: SessionTopicInfo,
                     timezone: str, storage: SessionStorage)->'ModeratorSession':

        # Mount session info
        session_info = SessionInfo(id=storage.session_id, topic=topic, local_timezone=timezone, dyad_id=dyad.id)
        await storage.update_session_info(session_info)
        return cls(dyad, storage)

    @classmethod
    async def restore_instance(cls, dyad: Dyad, storage: SessionStorage) -> Optional['ModeratorSession']:
        session_info = await storage.get_session_info()
        if session_info is None:
            # No session has been initialized.
            return None
        else:
            instance = ModeratorSession(dyad, storage)
            if session_info.status == SessionStatus.Started:
                # It has been started but somehow terminated.
                current_turn = await storage.get_latest_turn()
                if current_turn is None:
                    new_turn = DialogueTurn(session_id=storage.session_id, role=DialogueRole.Parent)
                    await storage.upsert_dialogue_turn(new_turn)
                elif current_turn.role == DialogueRole.Parent and current_turn.ended_timestamp is None:
                    pass
                else:
                    raise WrongSessionStatusError()

            
            return instance


    async def start(self) -> tuple[DialogueTurn, ParentGuideRecommendationResult]:

        session_info = await self.storage.get_session_info()

        if session_info.status == SessionStatus.Initial:
            session_info.status = SessionStatus.Started
            await self.storage.update_session_info(session_info)

            current_turn = await self.storage.get_latest_turn()
            if current_turn is None or current_turn.ended_timestamp is not None:
                new_turn = DialogueTurn(session_id=self.storage.session_id, role=DialogueRole.Parent)
                await self.__storage.upsert_dialogue_turn(new_turn)
                print(f"Initiate new turn. Turn id: {new_turn.id}, SessionInfo id: {self.storage.session_id}")
                current_turn = new_turn
            else:
                print(f"This session has already started. SessionInfo Id: {self.storage.session_id}")

            parent_guides = await self.__generate_parent_guide_recommendation()

            session_info = await self.storage.get_session_info()
            session_info.status = SessionStatus.Conversation
            await self.storage.update_session_info(session_info)

            return current_turn, parent_guides
        else:
            raise WrongSessionStatusError()


    async def terminate(self):
        self.cancel_all_async_tasks()
        session_info = await self.storage.get_session_info()
        session_info.ended_timestamp = get_timestamp()
        session_info.status = SessionStatus.Terminated
        await self.storage.update_session_info(session_info)
        await self.storage.dispose()


    async def current_speaker(self) -> DialogueRole | None:
        turn = await self.__storage.get_latest_turn()
        if turn is not None:
            return turn.role
        else:
            return None

    async def _switch_turn(self)->DialogueTurn:
        current_turn = await self.__storage.get_latest_turn()
        if current_turn.ended_timestamp is None:
            current_turn.ended_timestamp = get_timestamp()
            await self.storage.upsert_dialogue_turn(current_turn)
        next_turn = DialogueTurn(session_id=self.storage.session_id, role= DialogueRole.Parent if current_turn.role == DialogueRole.Child else DialogueRole.Child)
        await self.__storage.upsert_dialogue_turn(next_turn)
        return next_turn


    def cancel_all_async_tasks(self):
        print("Cancel all moderation session tasks.")
        self.__clear_parent_example_generation_tasks()
        if self.__dialogue_inspection_task_info is not None:
            self.__dialogue_inspection_task_info.task.cancel()

    def __clear_parent_example_generation_tasks(self):
        if self.__parent_example_generation_tasks is not None:
            for k, t in self.__parent_example_generation_tasks.tasks.items():
                if not t.task.done():
                    t.task.cancel()
            self.__parent_example_generation_tasks = None

    async def __parent_example_generate_func(self, dialogue: Dialogue, guide: ParentGuideElement, recommendation_id: str) -> ParentExampleMessage:
        if len(dialogue) == 0:
            message = self.__static_guide_factory.get_example_message(await self.session_topic(), self.__dyad, guide, recommendation_id)
        else:
            message = await self.__parent_example_generator.generate(self.__dyad.locale, dialogue, guide, recommendation_id)

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

    async def __generate_parent_guide_recommendation(self) -> ParentGuideRecommendationResult:

        current_turn = await self.storage.get_latest_turn()

        dialogue = await self.storage.get_dialogue()

        # Join a dialogue inspection task
        dialogue_inspection_result = None
        if self.__dialogue_inspection_task_info is not None:
            dialogue_inspection_result, task_id = await self.__dialogue_inspection_task_info.task
            if task_id != self.__dialogue_inspection_task_info.task_id:
                dialogue_inspection_result = None

        # Clear
        self.__dialogue_inspection_task_info = None

        session_topic = await self.session_topic()

        if len(dialogue) == 0:
            recommendation = self.__static_guide_factory.get_guide_recommendation(session_topic, self.__dyad, current_turn.id)
        else:
            recommendation = await self.__parent_guide_recommender.generate(current_turn.id, self.__dyad, session_topic, dialogue, dialogue_inspection_result)

        await self.__storage.add_parent_guide_recommendation_result(recommendation)

        # Invoke an example generation task in advance.
        self.__clear_parent_example_generation_tasks()
        self.__place_parent_example_generation_tasks(dialogue, recommendation)

        return recommendation

    @speaker(DialogueRole.Parent)
    async def submit_parent_message(self, parent_message: str) -> tuple[DialogueTurn, ChildCardRecommendationResult]:

        try:

            current_turn = await self.storage.get_latest_turn()

            # Clear if there is a pending example generation task.
            self.__clear_parent_example_generation_tasks()

            if self.locale == UserLocale.English:
                message_eng = parent_message
            else:
                print("Translate parent message..")
                message_eng = await self.__deepl_translator.translate(
                    text=parent_message,
                    source_lang="KO", target_lang="EN-US",
                    context="The message is from a parent to their child."
                )

                print("Translated parent message.")

            current_guide = await self.storage.get_latest_parent_guide_recommendation(turn_id=current_turn.id)
            if current_guide is None:
                # Load Initial guide
                pass

            new_message = DialogueMessage(role=DialogueRole.Parent,
                                          content_localized=parent_message,
                                          content=message_eng,
                                          turn_id=current_turn.id)

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

            session_topic = await self.session_topic()

            next_turn = await self._switch_turn()

            recommendation = await self.__child_card_recommender.generate(topic_info=session_topic,
                                                                          locale=self.__dyad.locale,
                                                                          parent_type=self.__dyad.parent_type,
                                                                          dialogue=dialogue, interim_cards=None,
                                                                          previous_recommendation=None,
                                                                          turn_id=next_turn.id
                                                                          )

            await self.__storage.add_card_recommendation_result(recommendation)

            await self.storage.add_interaction(Interaction(
                type=InteractionType.SubmitParentMessage,
                turn_id=current_turn.id,
                metadata=dict(
                    message_eng=message_eng,
                    message=parent_message,
                    next_turn_id=next_turn.id,
                    child_recommendation_id=recommendation.id
                )))

            return next_turn, recommendation
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
            current_turn = await self.storage.get_latest_turn()
            dialogue = await self.__storage.get_dialogue()

            interim_card_selection = await self.storage.get_latest_card_selection(turn_id=current_turn.id)
            prev_recommendation = await self.storage.get_latest_child_card_recommendation(turn_id=current_turn.id)

            interim_cards = (await self.get_card_info_from_identities(interim_card_selection.cards)) if interim_card_selection is not None else None

            session_topic = await self.session_topic()

            recommendation = await self.__child_card_recommender.generate(current_turn.id,
                                                                          self.__dyad.locale,
                                                                          self.__dyad.parent_type, session_topic, dialogue, interim_cards, prev_recommendation)

            await self.__storage.add_card_recommendation_result(recommendation)

            await self.storage.add_interaction(Interaction(
                type=InteractionType.RefreshChildCards,
                turn_id=current_turn.id,
                metadata=dict(
                    new_card_recommendation_id=recommendation.id
                )
            ))

            return recommendation
        except Exception as e:
            raise e

    @speaker(DialogueRole.Child)
    async def append_child_card(self, card_identity: CardIdentity) -> InterimCardSelection:
        try:
            current_turn = await self.storage.get_latest_turn()

            current_card_selection = await self.storage.get_latest_card_selection(turn_id=current_turn.id)
            new_card_selection = InterimCardSelection(
                turn_id=current_turn.id,
                cards=[*current_card_selection.cards, card_identity] if current_card_selection is not None else [card_identity])
            await self.storage.add_card_selection(new_card_selection)


            await self.storage.add_interaction(Interaction(
                type=InteractionType.AppendChildCard,
                turn_id=current_turn.id,
                metadata=dict(
                    new_card_selection_id=new_card_selection.id
                )
            ))

            return new_card_selection
        except Exception as e:
            raise e

    @speaker(DialogueRole.Child)
    async def pop_last_child_card(self) -> tuple[InterimCardSelection, ChildCardRecommendationResult]:
        try:
            current_turn = await self.storage.get_latest_turn()
            current_card_selection = await self.storage.get_latest_card_selection(turn_id=current_turn.id)

            if len(current_card_selection.cards) > 0:
                last_card = current_card_selection.cards[-1]
                new_card_selection = InterimCardSelection(turn_id=current_turn.id, cards=current_card_selection.cards[:-1])
                await self.storage.add_card_selection(new_card_selection)

                prev_recommendation = await self.storage.get_card_recommendation_result(last_card.recommendation_id)
                new_recommendation = ChildCardRecommendationResult(**prev_recommendation.model_dump(exclude={"id"}))
                await self.storage.add_card_recommendation_result(new_recommendation)
                
                await self.storage.add_interaction(Interaction(
                    type=InteractionType.RemoveLastChildCard,
                    turn_id=current_turn.id,
                    metadata=dict(
                        removed_card_id=last_card.id,
                        orig_card_selection_id=current_card_selection.id,
                        new_card_selection_id=new_card_selection.id
                    )
                ))

                return new_card_selection, new_recommendation
            else:
                recommendation = await self.storage.get_latest_child_card_recommendation(turn_id = current_turn.id)
                return current_card_selection, recommendation
        except Exception as e:
            raise e

    @speaker(DialogueRole.Child)
    async def confirm_child_card_selection(self) -> tuple[DialogueTurn, ParentGuideRecommendationResult]:
        try:
            current_turn = await self.storage.get_latest_turn()
            interim_card_selection = await self.storage.get_latest_card_selection(turn_id=current_turn.id)
            if interim_card_selection is not None:
                selected_cards = await self.get_card_info_from_identities(interim_card_selection.cards)
                await self.__storage.add_dialogue_message(DialogueMessage(
                    role=DialogueRole.Child,
                    content=selected_cards,
                    turn_id=current_turn.id
                ))
                next_turn = await self._switch_turn()

                parent_recommendation = await self.__generate_parent_guide_recommendation()

                await self.storage.add_interaction(Interaction(
                    type=InteractionType.ConfirmChildCardSelection,
                    turn_id=current_turn.id,
                    metadata=dict(
                        next_turn_id=next_turn.id,
                        confirmed_card_selection_id=interim_card_selection.id,
                        parent_recommendation_id=parent_recommendation.id
                        )
                ))

                return next_turn, parent_recommendation
            else:
                raise ValueError("No interim card selection.")

        except Exception as e:
            raise e

    @speaker(DialogueRole.Parent)
    async def request_parent_example_message(self, recommendation_id: str, guide_id: str) -> ParentExampleMessage:
        if (self.__parent_example_generation_tasks is not None
                and self.__parent_example_generation_tasks.recommendation_id == recommendation_id):
            example_message: ParentExampleMessage = await self.__parent_example_generation_tasks.tasks[guide_id].task
        else:
            example_message: ParentExampleMessage | None = await self.__storage.get_parent_example_message(recommendation_id,
                                                                                                    guide_id)
            if example_message is None:
                dialogue = await self.__storage.get_dialogue()
                recommendation = await self.__storage.get_parent_guide_recommendation_result(recommendation_id)
                guide = [guide for guide in recommendation.guides if guide.id == guide_id][0]
                example_message = await self.__parent_example_generate_func(dialogue, guide, recommendation.id)

        current_turn = await self.storage.get_latest_turn()

        await self.storage.add_interaction(Interaction(
            type=InteractionType.RequestParentExampleMessage,
            turn_id=current_turn.id,
            metadata=dict(
                recommendation_id=recommendation_id,
                guide_id=guide_id,
                example_message_id=example_message.id
            )
        ))

        return example_message

