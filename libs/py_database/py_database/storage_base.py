from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

class SQLStorageBase:

    __sql_session_maker: sessionmaker[AsyncSession]

    @classmethod
    def set_session_maker(cls, func: sessionmaker[AsyncSession]):
        cls.__sql_session_maker = func

    @classmethod
    def get_sessionmaker(cls)-> sessionmaker[AsyncSession]:
        return cls.__sql_session_maker()