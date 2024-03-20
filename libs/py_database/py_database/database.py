from .model import *
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

def create_database_engine(db_path: str, verbose: bool = False) -> AsyncEngine:
    return create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=verbose)


def get_async_session(engine: AsyncEngine) -> AsyncSession:
    return AsyncSession(
        bind=engine
    )


async def create_db_and_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
