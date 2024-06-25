from .models import *
from py_core.system.model import ParentType, ChildGender
from py_database.database import AsyncSession, make_async_session_maker, create_database_engine
from sqlmodel import select
from py_database.model import DyadORM

engine = create_database_engine("database.db", verbose=True)

db_sessionmaker = make_async_session_maker(engine)

async def with_db_session() -> AsyncSession:
    async with db_sessionmaker() as session:
        yield session


async def create_test_dyad() -> bool:
   async with db_sessionmaker() as db:
        async with db.begin():
            statement = select(DyadORM).where(DyadORM.alias == "test")
            result = await db.exec(statement)
            
            if result.one_or_none() is None:
                test_dyad = DyadORM(alias="test", child_name="다솜이", parent_type=ParentType.Mother, child_gender=ChildGender.Girl)
                dyad_login = DyadLoginCode(code="12345", dyad_id=test_dyad.id)
                db.add(test_dyad)
                db.add(dyad_login)
                print("Created test dyad with login code 12345.")
                return True
            else:
                return False