from typing import AsyncGenerator, Callable
from .model import *
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel, Field
from pydantic.fields import FieldInfo

def create_database_engine(db_path: str, verbose: bool = False) -> AsyncEngine:
    return create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=verbose)


def make_async_session_maker(engine: AsyncEngine) -> sessionmaker[AsyncSession]:
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def column_exists_in_db(engine: AsyncEngine, model: SQLModel, column_name: str)->bool: 
    async with engine.connect() as connection:
        result = await connection.execute(text(f"PRAGMA table_info({model.__tablename__})"))

        columns = [row[1] for row in result]

        return column_name in columns
    
async def add_column_to_table(engine: AsyncEngine, model: SQLModel, column_name: str, column_params: str, default_value: Optional[any]):
    async with engine.connect() as connection:
        await connection.execute(text(f"ALTER TABLE {model.__tablename__}\nADD COLUMN {column_name} {column_params} {('DEFAULT ' + default_value) if default_value is not None else ''}"))
    
async def migrate(engine: AsyncEngine):
    print("Run migration...")

    if (await column_exists_in_db(engine, DyadORM, "locale")) is False:
        # Add locale column
        await add_column_to_table(engine, DyadORM, "locale", "VARCHAR(7) NOT NULL", "Korean")
    
    return

async def create_db_and_tables(engine: AsyncEngine):

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    await migrate(engine)
