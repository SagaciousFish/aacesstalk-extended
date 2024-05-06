import sqlalchemy.exc
from chatlib.utils import env_helper
from chatlib.utils.time import get_timestamp
from jose import jwt
from sqlmodel import select

from backend import env_variables
from backend.database import DyadLoginCode, AsyncSession
from py_database.model import Dyad


async def get_dyad_list(session: AsyncSession) -> list[tuple[Dyad, DyadLoginCode]]:
    statement = (select(DyadLoginCode, Dyad)
                 .where(DyadLoginCode.dyad_id == Dyad.id))
    results = await session.exec(statement)
    return [row for row in results]


async def create_dyad(alias: str, child_name: str, session: AsyncSession) -> tuple[Dyad, DyadLoginCode]:
    dyad = Dyad(alias=alias, child_name=child_name)

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


async def login_with_code(login_code: str, session: AsyncSession) -> str:
    statement = (select(DyadLoginCode, Dyad)
                 .where(DyadLoginCode.code == login_code)
                 .where(DyadLoginCode.active == True)
                 .where(DyadLoginCode.dyad_id == Dyad.id)
                 .limit(1))
    results = await session.exec(statement)
    if results.first() is not None:
        _, dyad = results.first()
        print(f"Found a match dyad - {dyad.id} / child: {dyad.child_name}")

        # Make JWT
        issued_at = get_timestamp()
        to_encode = {
            "sub": dyad.id,
            "alias": dyad.alias,
            "child_name": dyad.child_name,
            "iat": issued_at,
            "exp": issued_at + (365 * 24 * 3600 * 1000)  # 1 year
        }
        access_token = jwt.encode(to_encode, env_helper.get_env_variable(env_variables.AUTH_SECRET))
        return access_token
    else:
        raise ValueError("No such dyadic user with the code.")


async def get_dyad_by_id(id: str, session: AsyncSession) -> Dyad | None:
    statement = (select(Dyad)
                 .where(Dyad.id == id)
                 .limit(1))
    results = await session.exec(statement)
    return results.first()
