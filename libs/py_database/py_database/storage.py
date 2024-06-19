from typing import AsyncGenerator, Callable
from pydantic import validate_call
from sqlmodel import select, col, delete, update
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from py_core.system.model import DialogueTurn, Interaction, ParentGuideRecommendationResult, ChildCardRecommendationResult, Dialogue, \
    DialogueMessage, ParentExampleMessage, InterimCardSelection, SessionInfo
from py_core.system.storage import SessionStorage
from py_database.model import (DialogueMessageORM, DialogueTurnORM, InteractionORM, SessionORM,
                               ChildCardRecommendationResultORM,
                               InterimCardSelectionORM,
                               ParentGuideRecommendationResultORM,
                               ParentExampleMessageORM, SessionIdMixin)


class SQLSessionStorage(SessionStorage):

    __sql_session_maker: sessionmaker[AsyncSession]

    @classmethod
    def set_session_maker(cls, func: sessionmaker[AsyncSession]):
        cls.__sql_session_maker = func

    @classmethod
    async def _load_session_info(cls, session_id: str) -> SessionInfo | None:
        async with cls.__sql_session_maker() as db:
            return await cls.__load_session_info_impl(db, session_id)

    @classmethod        
    async def __load_session_info_impl(cls, db: AsyncSession, session_id: str) -> SessionInfo | None:
        print("Find session with id", session_id)
        statement = select(SessionORM).where(SessionORM.id == session_id)
        results = await db.exec(statement)
        session_orm = results.first()
        print("Session orm:", session_orm)
        if session_orm is not None:
            return session_orm.to_data_model()
        else:
            return None


    @validate_call
    def __init__(self, session_id: str):
        super().__init__(session_id)


    async def add_dialogue_message(self, message: DialogueMessage):
        async with self.__sql_session_maker() as db:
            async with db.begin():
                db.add(DialogueMessageORM.from_data_model(self.session_id, message))

    async def get_dialogue(self) -> Dialogue:
        async with self.__sql_session_maker() as db:
            statement = select(DialogueMessageORM).where(DialogueMessageORM.session_id == self.session_id).order_by(
                col(DialogueMessageORM.timestamp).desc())
            results = await db.exec(statement)
            return [msg.to_data_model() for msg in results]

    async def get_latest_dialogue_message(self) -> DialogueMessage | None:
        async with self.__sql_session_maker() as db:
            statement = select(DialogueMessageORM).where(DialogueMessageORM.session_id == self.session_id).order_by(
                col(DialogueMessageORM.timestamp).desc()).limit(1)
            results = await db.exec(statement)

            f = results.first()
            if f is not None:
                return f.to_data_model()
            else:
                return None

    async def add_card_recommendation_result(self, result: ChildCardRecommendationResult):
        async with self.__sql_session_maker() as db:
            async with db.begin():
                db.add(ChildCardRecommendationResultORM.from_data_model(self.session_id, result))

    async def add_parent_guide_recommendation_result(self, result: ParentGuideRecommendationResult):
        async with self.__sql_session_maker() as db:
            async with db.begin():
                db.add(ParentGuideRecommendationResultORM.from_data_model(self.session_id, result))
        
    async def get_card_recommendation_result(self, recommendation_id: str) -> ChildCardRecommendationResult | None:
        async with self.__sql_session_maker() as db:
            statement = select(ChildCardRecommendationResultORM).where(
                ChildCardRecommendationResultORM.id == recommendation_id)
            result = await db.exec(statement)
            orm: ChildCardRecommendationResultORM | None = result.first()
            return orm.to_data_model() if orm is not None else None

    async def get_parent_guide_recommendation_result(self,
                                                     recommendation_id: str) -> ParentGuideRecommendationResult | None:
        async with self.__sql_session_maker() as db:
            statement = select(ParentGuideRecommendationResultORM).where(
                ParentGuideRecommendationResultORM.id == recommendation_id)
            result = await db.exec(statement)
            orm: ParentGuideRecommendationResultORM | None = result.first()
            return orm.to_data_model() if orm is not None else None

    async def add_parent_example_message(self, message: ParentExampleMessage):
        async with self.__sql_session_maker() as db:
            async with db.begin():
                db.add(ParentExampleMessageORM.from_data_model(self.session_id, message))

    async def get_parent_example_message(self, recommendation_id: str, guide_id: str) -> ParentExampleMessage | None:
        async with self.__sql_session_maker() as db:
            statement = (select(ParentExampleMessageORM)
                        .where(ParentExampleMessageORM.recommendation_id == recommendation_id)
                        .where(ParentExampleMessageORM.guide_id == guide_id))
            result = await db.exec(statement)
            orm: ParentExampleMessageORM | None = result.first()
            return orm.to_data_model() if orm is not None else None

    async def add_card_selection(self, selection: InterimCardSelection):
        async with self.__sql_session_maker() as db:
            async with db.begin():
                db.add(InterimCardSelectionORM.from_data_model(self.session_id, selection))

    async def __get_latest_model(self, db: AsyncSession, model: type[SessionIdMixin], timestamp_column: any = None, turn_id: str | None = None) -> SessionIdMixin | None:

        if timestamp_column is None:
            timestamp_column = model.timestamp


        statement = select(model).where(model.session_id == self.session_id)

        if turn_id is not None:
            statement = statement.where(model.turn_id == turn_id)

        statement = (statement.order_by(col(timestamp_column).desc()).limit(1))
        results = await db.exec(statement)
        first = results.first()
        if first is not None:
            return first
        else:
            return None

    async def get_latest_card_selection(self, turn_id=None) -> InterimCardSelection | None:
        async with self.__sql_session_maker() as db:
            d = await self.__get_latest_model(db, InterimCardSelectionORM, turn_id=turn_id)
            if d is not None and isinstance(d, InterimCardSelectionORM):
                return d.to_data_model()
            else:
                return None

    async def get_latest_parent_guide_recommendation(self, turn_id=None) -> ParentGuideRecommendationResult | None:
        async with self.__sql_session_maker() as db:
            d = await self.__get_latest_model(db, ParentGuideRecommendationResultORM, turn_id=turn_id)
            if d is not None and isinstance(d, ParentGuideRecommendationResultORM):
                return d.to_data_model()
            else:
                return None

    async def get_latest_child_card_recommendation(self, turn_id=None) -> ChildCardRecommendationResult | None:
        async with self.__sql_session_maker() as db:
            d = await self.__get_latest_model(db, ChildCardRecommendationResultORM, turn_id=turn_id)
            if d is not None and isinstance(d, ChildCardRecommendationResultORM):
                return d.to_data_model()
            else:
                return None

    async def delete_entities(self):
        async with self.__sql_session_maker() as db:
            async with db.begin():
                for model in [DialogueMessageORM, ChildCardRecommendationResultORM, InterimCardSelectionORM, ParentGuideRecommendationResultORM, ParentExampleMessageORM]:
                    rows = await db.exec(select(model).where(model.session_id == self.session_id))
                    for row in rows:
                        await db.delete(row)

    async def update_session_info(self, info: SessionInfo):
        async with self.__sql_session_maker() as db:
            async with db.begin():
                orig_orm = await self.__load_session_info_impl(db, info.id)
                if orig_orm is None:
                    db.add(SessionORM.from_data_model(info))
                else:
                    # Update
                    statement = update(SessionORM).where(
                        SessionORM.id == info.id
                    ).values(**SessionORM.from_data_model(info).model_dump(exclude={"id", "dyad_id"}))
                    await db.exec(statement)

    async def upsert_dialogue_turn(self, turn: DialogueTurn):
        async with self.__sql_session_maker() as db:
            async with db.begin():
                orig_orm = await db.get(DialogueTurnORM, turn.id)
                if orig_orm is not None:
                    # Update
                    statement = update(DialogueTurnORM).where(
                        DialogueTurnORM.id == turn.id
                    ).values(**turn.model_dump(exclude={"id"}))
                    await db.exec(statement)
                else:
                    # Insert
                    db.add(DialogueTurnORM.from_data_model(turn, self.session_id))

    async def get_latest_turn(self) -> DialogueTurn | None:
        async with self.__sql_session_maker() as db:
            d = await self.__get_latest_model(db, DialogueTurnORM, DialogueTurnORM.started_timestamp)
            if d is not None and isinstance(d, DialogueTurnORM):
                return d.to_data_model()
            else:
                return None

    async def add_interaction(self, interaction: Interaction):
        async with self.__sql_session_maker() as db:
            async with db.begin():
                db.add(InteractionORM.from_data_model(interaction, self.session_id))

