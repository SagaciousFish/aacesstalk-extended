from abc import ABC, abstractmethod
from typing import Callable
from sqlmodel import SQLModel, select, col, delete, update
from pydantic import validate_call

from py_core.system.model import DialogueTurn, Interaction, ParentGuideRecommendationResult, ChildCardRecommendationResult, Dialogue, \
    DialogueMessage, ParentExampleMessage, InterimCardSelection, DialogueRole, SessionInfo
from py_core.system.storage import SessionStorage
from py_database.model import (DialogueMessageORM, DialogueTurnORM, InteractionORM, TimestampColumnMixin,
                               SessionORM,
                               ChildCardRecommendationResultORM,
                               InterimCardSelectionORM,
                               ParentGuideRecommendationResultORM,
                               ParentExampleMessageORM, SessionIdMixin)
from py_database.database import AsyncSession


class SQLSessionStorage(SessionStorage, ABC):
    
    @classmethod
    @abstractmethod
    async def _load_session_info(cls, session_id: str) -> SessionInfo | None:
        pass


    @validate_call
    def __init__(self, sql_session_maker: Callable[[], AsyncSession], session_id: str):
        super().__init__(session_id)
        self.__sql_session_maker = sql_session_maker
        self.__current_sql_session: AsyncSession | None = None

    @property
    def _sql_session(self)->AsyncSession:
        if self.__current_sql_session is None or self.__current_sql_session.is_active is False:
            self.__current_sql_session = self.__sql_session_maker()

        return self.__current_sql_session


    @classmethod
    @validate_call
    async def restore_instance(cls, id: str, params: Callable[[], AsyncSession]) -> SessionStorage | None:
        async with params() as db:
            session_orm = await db.get(SessionORM, id)
            if session_orm is not None:
                return SQLSessionStorage(params, session_orm.to_data_model())
            else:
                return None


    async def add_dialogue_message(self, message: DialogueMessage):
        self._sql_session.add(DialogueMessageORM.from_data_model(self.session_id, message))
        await self._sql_session.commit()

    async def get_dialogue(self) -> Dialogue:
        statement = select(DialogueMessageORM).where(DialogueMessageORM.session_id == self.session_id).order_by(
            col(DialogueMessageORM.timestamp).desc())
        results = await self._sql_session.exec(statement)
        return [msg.to_data_model() for msg in results]

    async def get_latest_dialogue_message(self) -> DialogueMessage | None:
        statement = select(DialogueMessageORM).where(DialogueMessageORM.session_id == self.session_id).order_by(
            col(DialogueMessageORM.timestamp).desc()).limit(1)
        results = await self._sql_session.exec(statement)

        f = results.first()
        if f is not None:
            return f.to_data_model()
        else:
            return None

    async def add_card_recommendation_result(self, result: ChildCardRecommendationResult):
        self._sql_session.add(ChildCardRecommendationResultORM.from_data_model(self.session_id, result))
        await self._sql_session.commit()

    async def add_parent_guide_recommendation_result(self, result: ParentGuideRecommendationResult):
        self._sql_session.add(ParentGuideRecommendationResultORM.from_data_model(self.session_id, result))
        await self._sql_session.commit()

    async def get_card_recommendation_result(self, recommendation_id: str) -> ChildCardRecommendationResult | None:
        statement = select(ChildCardRecommendationResultORM).where(
            ChildCardRecommendationResultORM.id == recommendation_id)
        result = await self._sql_session.exec(statement)
        orm: ChildCardRecommendationResultORM | None = result.first()
        return orm.to_data_model() if orm is not None else None

    async def get_parent_guide_recommendation_result(self,
                                                     recommendation_id: str) -> ParentGuideRecommendationResult | None:
        statement = select(ParentGuideRecommendationResultORM).where(
            ParentGuideRecommendationResultORM.id == recommendation_id)
        result = await self._sql_session.exec(statement)
        orm: ParentGuideRecommendationResultORM | None = result.first()
        return orm.to_data_model() if orm is not None else None

    async def add_parent_example_message(self, message: ParentExampleMessage):
        self._sql_session.add(ParentExampleMessageORM.from_data_model(self.session_id, message))
        await self._sql_session.commit()

    async def get_parent_example_message(self, recommendation_id: str, guide_id: str) -> ParentExampleMessage | None:
        statement = (select(ParentExampleMessageORM)
                     .where(ParentExampleMessageORM.recommendation_id == recommendation_id)
                     .where(ParentExampleMessageORM.guide_id == guide_id))
        result = await self._sql_session.exec(statement)
        orm: ParentExampleMessageORM | None = result.first()
        return orm.to_data_model() if orm is not None else None

    async def add_card_selection(self, selection: InterimCardSelection):
        self._sql_session.add(InterimCardSelectionORM.from_data_model(self.session_id, selection))
        await self._sql_session.commit()

    async def __get_latest_model(self, model: type[SessionIdMixin], timestamp_column: any = None) -> SessionIdMixin | None:

        if timestamp_column is None:
            timestamp_column = model.timestamp

        statement = (select(model)
                         .where(model.session_id == self.session_id)
                         .order_by(col(timestamp_column).desc()).limit(1))
        results = await self._sql_session.exec(statement)
        first = results.first()
        if first is not None:
            return first
        else:
            return None

    async def get_latest_card_selection(self) -> InterimCardSelection | None:
        d = await self.__get_latest_model(InterimCardSelectionORM)
        if d is not None and isinstance(d, InterimCardSelectionORM):
            return d.to_data_model()
        else:
            return None

    async def get_latest_parent_guide_recommendation(self) -> ParentGuideRecommendationResult | None:
        d = await self.__get_latest_model(ParentGuideRecommendationResultORM)
        if d is not None and isinstance(d, ParentGuideRecommendationResultORM):
            return d.to_data_model()
        else:
            return None

    async def get_latest_child_card_recommendation(self) -> ChildCardRecommendationResult | None:
        d = await self.__get_latest_model(ChildCardRecommendationResultORM)
        if d is not None and isinstance(d, ChildCardRecommendationResultORM):
            return d.to_data_model()
        else:
            return None

    async def delete_entities(self):
        async with self.__sql_session_maker() as s:
            for model in [DialogueMessageORM, ChildCardRecommendationResultORM, InterimCardSelectionORM, ParentGuideRecommendationResultORM, ParentExampleMessageORM]:
                await s.exec(delete(model).where(DialogueMessageORM.session_id == self.session_id))
            await s.commit()

    async def update_session_info(self, info: SessionInfo):
        orig_orm = await self._load_session_info(info.id)
        if orig_orm is None:
            self._sql_session.add(SessionORM.from_data_model(info))
            await self._sql_session.commit()
        else:
            # Update
            statement = update(SessionORM).where(
                SessionORM.id == info.id
            ).values(**SessionORM.from_data_model(info).model_dump(exclude={"id", "dyad_id"}))
            await self._sql_session.exec(statement)

    async def upsert_dialogue_turn(self, turn: DialogueTurn):
        orig_orm = await self._sql_session.get(DialogueTurnORM, turn.id)
        if orig_orm is not None:
            # Update
            statement = update(DialogueTurnORM).where(
                DialogueTurnORM.id == turn.id
            ).values(**turn.model_dump(exclude={"id"}))
            await self._sql_session.exec(statement)
        else:
            # Insert
            self._sql_session.add(DialogueTurnORM.from_data_model(turn, self.session_id))
            await self._sql_session.commit()

    async def get_latest_turn(self) -> DialogueTurn | None:
        d = await self.__get_latest_model(DialogueTurnORM, DialogueTurnORM.started_timestamp)
        if d is not None and isinstance(d, DialogueTurnORM):
            return d.to_data_model()
        else:
            return None

    async def add_interaction(self, interaction: Interaction):
        self._sql_session.add(InteractionORM.from_data_model(interaction, self.session_id))
        await self._sql_session.commit()

