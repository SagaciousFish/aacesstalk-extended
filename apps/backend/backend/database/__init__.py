from .models import *
from py_core.system.model import ParentType
from py_database.database import AsyncSession, get_async_session, create_database_engine
from sqlmodel import select
from py_database.model import DyadORM

engine = create_database_engine("database.db", verbose=True)

async def with_db_session() -> AsyncSession:
    async with get_async_session(engine) as session:
        yield session


async def create_test_dyad() -> bool:
   async with get_async_session(engine) as session:
        statement = select(DyadORM).where(DyadORM.alias == "test")
        result = await session.exec(statement)
        
        if result.one_or_none() is None:
            test_dyad = DyadORM(alias="test", child_name="다솜이", parent_type=ParentType.Mother)
            dyad_login = DyadLoginCode(code="12345", dyad_id=test_dyad.id)
            session.add(test_dyad)
            session.add(dyad_login)
            await session.commit()
            print("Created test dyad with login code 12345.")
            return True
        else:
            return False