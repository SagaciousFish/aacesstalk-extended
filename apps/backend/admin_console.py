import asyncio
from enum import StrEnum
import questionary
from chatlib.utils.cli import make_non_empty_string_validator
from backend.crud.dyad.account import create_dyad, get_dyad_list
from backend.database import engine
from py_database.database import create_db_and_tables, get_async_session, AsyncSession


class ConsoleMenu(StrEnum):
    CreateDyad = "Create dyad"
    ListDyad = "Show dyad list"
    Exit = "Exit"


async def _create_dyad():
    async with AsyncSession(engine) as session:
        alias = await questionary.text(
            message="Enter dyad alias:",
            validate=make_non_empty_string_validator("Dyad alias cannot be empty.")).ask_async()
        child_name = await questionary.text(
            message="Enter child name:",
            validate=make_non_empty_string_validator("Child name cannot be empty.")).ask_async()
        
        parent_type = await questionary.select("Select parent type.", ["Mother", "Father"], "Mother").ask_async()
        
        confirm = await questionary.confirm(f"Create a dyad with alias \"{alias}\" and a child name \"{child_name}\" and {parent_type}?").ask_async()

        if confirm:
            dyad, dyad_code = await create_dyad(alias, child_name, parent_type, session)
            print(f"Created a dyad {dyad.alias} (Child: {dyad.child_name}, Parent type: {dyad.parent_type}). Code: {dyad_code.code}")

async def _list_dyad():
    async with AsyncSession(engine) as session:
        l = await get_dyad_list(session)
        print(f"{len(l)} dyads in the database.")
        print(l)

async def _run_console_loop():

    await create_db_and_tables(engine)

    while True:
        menu = await questionary.select("Select a command.", [menu for menu in ConsoleMenu]).ask_async()

        if menu is ConsoleMenu.CreateDyad:
            await _create_dyad()
        if menu is ConsoleMenu.ListDyad:
            await _list_dyad()
        elif menu is ConsoleMenu.Exit:
            print("Bye.")
            break



if __name__ == "__main__":
    print("Launching admin console...")
    asyncio.run(_run_console_loop())
