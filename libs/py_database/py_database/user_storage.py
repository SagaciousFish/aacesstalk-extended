from py_core.system.model import CardCategory, UserDefinedCardInfo
from py_core.system.storage import UserStorage

from py_database.model import UserDefinedCardInfoORM
from py_database.storage_base import SQLStorageBase
from sqlalchemy import select, func

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
            return result.first()