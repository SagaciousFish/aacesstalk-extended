from sqlmodel import select, col, delete

from py_core.system.model import ParentGuideRecommendationResult, ChildCardRecommendationResult, Dialogue, \
    DialogueMessage, ParentExampleMessage, InterimCardSelection, DialogueRole, Session
from py_core.system.storage import SessionStorage
from py_database.model import (DialogueMessage as DialogueMessageORM,
                               Session as SessionORM,
                               ChildCardRecommendationResult as ChildCardRecommendationResultORM,
                               InterimCardSelection as InterimCardSelectionORM,
                               ParentGuideRecommendationResult as ParentGuideRecommendationResultORM,
                               ParentExampleMessage as ParentExampleMessageORM, SessionIdMixin, TimestampColumnMixin)
from py_database.database import AsyncSession

class TimeStampAndSessionChildModel(SessionIdMixin, TimestampColumnMixin):
    pass

class SQLSessionStorage(SessionStorage):

    def __init__(self, sql_session: AsyncSession, session: Session):
        super().__init__(session)
        self.__sql_session = sql_session

    @property
    def _sql_session(self)->AsyncSession:
        print(f"DB session active: {self.__sql_session.is_active}")
        return self.__sql_session

    
    @classmethod
    async def restore_instance(cls, id: str, params: AsyncSession) -> SessionStorage | None:
        session_orm = await params.get(SessionORM, id)
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

    async def __get_latest_model(self, model: type[TimeStampAndSessionChildModel]) -> TimeStampAndSessionChildModel | None:
        statement = (select(model)
                         .where(model.session_id == self.session_id)
                         .order_by(col(model.timestamp).desc()).limit(1))
        results = await self._sql_session.exec(statement)
        first = results.first()
        if first is not None:
            return first
        else:
            return None

    async def get_latest_card_selection(self) -> InterimCardSelection | None:
        d = await self.__get_latest_model(InterimCardSelectionORM, latest_role=DialogueRole.Parent)
        if d is not None and isinstance(d, InterimCardSelectionORM):
            return d.to_data_model()
        else:
            return None

    async def get_latest_parent_guide_recommendation(self) -> ParentGuideRecommendationResult | None:
        d = await self.__get_latest_model(ParentGuideRecommendationResultORM, latest_role=DialogueRole.Child)
        if d is not None and isinstance(d, ParentGuideRecommendationResultORM):
            return d.to_data_model()
        else:
            return None

    async def get_latest_child_card_recommendation(self) -> ChildCardRecommendationResult | None:
        d = await self.__get_latest_model(ChildCardRecommendationResultORM, latest_role=DialogueRole.Parent)
        if d is not None and isinstance(d, ChildCardRecommendationResultORM):
            return d.to_data_model()
        else:
            return None

    async def delete_entities(self):
        with self._sql_session.begin():
            for model in [DialogueMessageORM, ChildCardRecommendationResultORM, InterimCardSelectionORM, ParentGuideRecommendationResultORM, ParentExampleMessageORM]:
                await self._sql_session.exec(delete(model).where(DialogueMessageORM.session_id == self.session_id))


            