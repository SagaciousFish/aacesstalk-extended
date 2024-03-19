from typing import Type

from sqlmodel import select, col, SQLModel

from py_core.system.model import ParentGuideRecommendationResult, ChildCardRecommendationResult, Dialogue, \
    DialogueMessage
from py_core.system.storage import SessionStorage
from py_database.model import DialogueMessage as DialogueMessageORM, ChildCardRecommendationResult as ChildCardRecommendationResultORM, ParentGuideRecommendationResult as ParentGuideRecommendationResultORM
from py_database.database import AsyncSession


class SQLSessionStorage(SessionStorage):
    def __init__(self, sql_session: AsyncSession, session_id: str | None = None):
        super().__init__(session_id)
        self.__sql_session = sql_session

    async def add_dialogue_message(self, message: DialogueMessage):
        self.__sql_session.add(DialogueMessageORM.from_data_model(self.session_id, message))
        await self.__sql_session.commit()

    async def get_dialogue(self) -> Dialogue:
        statement = select(DialogueMessageORM).where(DialogueMessageORM.session_id == self.session_id).order_by(col(DialogueMessageORM.timestamp).desc())
        results = await self.__sql_session.execute(statement)
        return [msg.to_dialogue_message() for msg in results]

    async def add_card_recommendation_result(self, result: ChildCardRecommendationResult):
        self.__sql_session.add(ChildCardRecommendationResultORM.from_data_model(result))
        await self.__sql_session.commit()

    async def add_parent_guide_recommendation_result(self, result: ParentGuideRecommendationResult):
        self.__sql_session.add(ParentGuideRecommendationResultORM.from_data_model(result))
        await self.__sql_session.commit()

    async def get_card_recommendation_result(self, recommendation_id: str) -> ChildCardRecommendationResult | None:
        statement = select(ChildCardRecommendationResultORM).where(ChildCardRecommendationResultORM.id == recommendation_id)
        result = await self.__sql_session.execute(statement)
        orm: ChildCardRecommendationResultORM | None = result.first()
        return orm.to_data_model() if orm is not None else None

    async def get_parent_guide_recommendation_result(self,
                                                     recommendation_id: str) -> ParentGuideRecommendationResult | None:
        statement = select(ParentGuideRecommendationResultORM).where(ParentGuideRecommendationResultORM.id == recommendation_id)
        result = await self.__sql_session.execute(statement)
        orm: ParentGuideRecommendationResultORM | None = result.first()
        return orm.to_data_model() if orm is not None else None
