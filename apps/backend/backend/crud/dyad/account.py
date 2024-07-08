from chatlib.utils import env_helper
from chatlib.utils.time import get_timestamp
import jwt
from sqlmodel import select

from backend import env_variables
from backend.database import DyadLoginCode, AsyncSession
from py_database.model import DyadORM, ParentType, ChildGender


async def get_dyad_list(session: AsyncSession) -> list[tuple[DyadORM, DyadLoginCode]]:
    statement = (select(DyadLoginCode, DyadORM)
                 .where(DyadLoginCode.dyad_id == DyadORM.id))
    results = await session.exec(statement)
    return [row for row in results]


async def create_dyad(alias: str, child_name: str, parent_type: ParentType, child_gender: ChildGender, session: AsyncSession) -> tuple[DyadORM, DyadLoginCode]:
    dyad = DyadORM(alias=alias, child_name=child_name, parent_type=parent_type, child_gender=child_gender)

    print(dyad)

    session.add(dyad)
    await session.commit()

    await session.refresh(dyad)

    dyad_code = DyadLoginCode(dyad_id=dyad.id)
    session.add(dyad_code)
    await session.commit()

    # Refresh objects before returning
    await session.refresh(dyad_code)
    await session.refresh(dyad)

    return dyad, dyad_code


async def login_with_code(login_code: str, session: AsyncSession) -> tuple[str, DyadORM]:
    statement = (select(DyadLoginCode, DyadORM)
                 .where(DyadLoginCode.code == login_code)
                 .where(DyadLoginCode.active == True)
                 .where(DyadLoginCode.dyad_id == DyadORM.id)
                 .limit(1))
    results = await session.exec(statement)
    first_row = results.first()
    if first_row is not None:
        _, dyad = first_row
        print(f"Found a match dyad - {dyad.id} / child: {dyad.child_name}")

        # Make JWT
        issued_at = get_timestamp()
        to_encode = {
            "sub": dyad.id,
            "alias": dyad.alias,
            "child_name": dyad.child_name,
            "child_gender": dyad.child_gender,
            "parent_type": dyad.parent_type,
            "iat": issued_at/1000,
            "exp": (issued_at + (365 * 24 * 3600 * 1000))/1000  # 1 year
        }
        access_token = jwt.encode(to_encode, env_helper.get_env_variable(env_variables.AUTH_SECRET), algorithm='HS256')
        return access_token, dyad
    else:
        raise ValueError("No such dyadic user with the code.")


async def get_dyad_by_id(id: str, session: AsyncSession) -> DyadORM | None:
    statement = (select(DyadORM)
                 .where(DyadORM.id == id)
                 .limit(1))
    results = await session.exec(statement)
    return results.first()