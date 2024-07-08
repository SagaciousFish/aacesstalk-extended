from py_core.system.model import CardCategory, FreeTopicDetail, UserDefinedCardInfo
from py_core.system.storage import UserStorage

from py_database.model import UserDefinedCardInfoORM, FreeTopicDetailORM
from py_database.storage_base import SQLStorageBase
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

class SQLUserStorage(UserStorage, SQLStorageBase):

    async def register_user_defined_card(self, info: UserDefinedCardInfo):
        async with self.get_sessionmaker() as db:
            async with db.begin():
                db.add(UserDefinedCardInfoORM.from_data_model(info, self.user_id))

    async def get_user_defined_cards(self) -> list[UserDefinedCardInfo]:
        async with self.get_sessionmaker() as db:
            subquery = select(
                UserDefinedCardInfoORM.dyad_id,
                UserDefinedCardInfoORM.label_localized, 
                UserDefinedCardInfoORM.category, 
                func.max(UserDefinedCardInfoORM.timestamp).label('max_timestamp')
                ).where(
                    UserDefinedCardInfoORM.dyad_id == self.user_id
                ).group_by(UserDefinedCardInfoORM.label_localized, UserDefinedCardInfoORM.category
                ).alias('subquery')
            
            query = select(UserDefinedCardInfoORM).join(
                subquery, 
                (UserDefinedCardInfoORM.dyad_id == subquery.c.dyad_id) & 
                (UserDefinedCardInfoORM.label_localized == subquery.c.label_localized) &
                (UserDefinedCardInfoORM.category == subquery.c.category) &
                (UserDefinedCardInfoORM.timestamp == subquery.c.timestamp)
            ).where(UserDefinedCardInfoORM.dyad_id == self.user_id)
            
            result = await db.exec(query)
            print(result)

            return []


    async def query_user_defined_card(self, category: CardCategory, label_localized: str) -> UserDefinedCardInfo | None:
        pass

    async def get_user_defined_card(self, id: str) -> UserDefinedCardInfo | None:
        async with self.get_sessionmaker() as db:
            statement = select(UserDefinedCardInfoORM).where(UserDefinedCardInfoORM.dyad_id == self.user_id, UserDefinedCardInfoORM.id == id).limit(1)

            result = await db.exec(statement)
            first_orm: UserDefinedCardInfoORM = result.first()
            
            return first_orm.to_data_model() if first_orm is not None else None

    async def upsert_free_topic_detail(self, detail: FreeTopicDetail):
        async with self.get_sessionmaker() as db:
            db: AsyncSession = db
            statement = select(FreeTopicDetailORM).where(FreeTopicDetailORM.dyad_id == self.user_id, FreeTopicDetailORM.id == detail.id).limit(1)
            result = await db.exec(statement)
            orm: FreeTopicDetailORM = result.one()
            async with db.begin():
                if orm is not None:
                    updated = orm.sqlmodel_update(detail.model_dump(exclude={"id"}))
                    db.add(updated)
                else:
                    db.add(detail)
                
                await db.commit()


    async def get_free_topic_details(self) -> list[FreeTopicDetail]:
        async with self.get_sessionmaker() as db:
            db: AsyncSession = db
            statement = select(FreeTopicDetailORM).where(FreeTopicDetailORM.dyad_id == self.user_id)

            result = await db.exec(statement)

            return [orm.to_data_model() for orm in result]

    async def remove_free_topic_detail(self, id: str):
        async with self.get_sessionmaker() as db:
            async with db.begin():
                db: AsyncSession = db
                orm = await db.get(FreeTopicDetailORM, id)
                if orm is not None:
                    await db.delete(orm)

    async def get_free_topic_detail(self, id: str) -> FreeTopicDetail | None:
        async with self.get_sessionmaker() as db:
            db: AsyncSession = db
            orm = await db.get(FreeTopicDetailORM, id)
            if orm is not None:
                return orm.to_data_model()
            else:
                return None


