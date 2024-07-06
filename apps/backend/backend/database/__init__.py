from .models import *
from py_core.system.model import ParentType, ChildGender
from py_database.database import AsyncSession, make_async_session_maker, create_database_engine
from sqlmodel import select
from py_database.model import DyadORM, FreeTopicDetailORM

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
            test_dyad = result.one_or_none()
            if test_dyad is None:
                test_dyad = DyadORM(alias="test", child_name="다솜이", parent_type=ParentType.Mother, child_gender=ChildGender.Girl)
                dyad_login = DyadLoginCode(code="12345", dyad_id=test_dyad.id)
                db.add(test_dyad)
                db.add(dyad_login)
                print("Created test dyad with login code 12345.")
                return True
            else:
                return False
            
async def create_test_freetopics() -> bool:
    async with db_sessionmaker() as db:
        async with db.begin():
            result = await db.exec(select(DyadORM).where(DyadORM.alias == "test"))
            test_dyad = result.one_or_none()
            if test_dyad is not None:
                statement = select(FreeTopicDetailORM).where(FreeTopicDetailORM.dyad_id == test_dyad.id)
                result = await db.exec(statement)
                    
                if result.first() is None:
                    topic_1 = FreeTopicDetailORM(dyad_id=test_dyad.id, subtopic="티니핑", subtopic_description="About the child's favorite animation characters, Teenieping.")
                    topic_2 = FreeTopicDetailORM(dyad_id=test_dyad.id, subtopic="공룡", subtopic_description="About dinosaurs that the child likes.")
                    topic_3 = FreeTopicDetailORM(dyad_id=test_dyad.id, subtopic="레고", subtopic_description="About Lego toy brick series that the child likes.")
                    db.add(topic_1)
                    db.add(topic_2)
                    db.add(topic_3)
                    print("Added free topics for dyad.")
                    return True
                else:
                    return False