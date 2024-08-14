
from sqlalchemy import func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar


async def query_count(db: AsyncSession, query: SelectOfScalar) -> int:
    count_q = query.with_only_columns(func.count()).order_by(None).select_from(*query.froms)
    iterator = await db.exec(count_q)
    for count in iterator:
        print("Count : ", count)
        return count
    return 0