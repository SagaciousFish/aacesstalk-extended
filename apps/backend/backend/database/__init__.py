from .models import *
from py_database.database import AsyncSession, get_async_session, create_database_engine

engine = create_database_engine("database.db", verbose=True)

async def get_db_session() -> AsyncSession:
    async with get_async_session(engine) as session:
        yield session
