from os import path, getcwd

import questionary
from dotenv import find_dotenv, set_key
from chatlib.utils.cli import make_non_empty_string_validator
from chatlib.global_config import GlobalConfig

from backend import env_variables
from py_core.system.moderator import ModeratorSession
from chatlib.utils import env_helper

if __name__ == "__main__":
    GlobalConfig.is_cli_mode = True

    ModeratorSession.assert_authorize()

    env_file = find_dotenv()
    if not path.exists(env_file):
        env_file = open(path.join(getcwd(), '.env'), 'w')
        env_file.close()
        env_file = find_dotenv()

    if env_helper.get_env_variable(env_variables.AUTH_SECRET) is None:
        auth_secret = questionary.text("Insert auth secret (Any random string).", default="Naver1784", validate=make_non_empty_string_validator("Put a string with length > 0.")).ask()
        set_key(env_file, env_variables.AUTH_SECRET, auth_secret)

    print("Setup complete.")
