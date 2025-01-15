from os import path, getcwd
import questionary
from dotenv import find_dotenv, set_key
from chatlib.utils.cli import make_non_empty_string_validator
from chatlib.global_config import GlobalConfig

from backend import env_variables
from py_core import env_variables as core_env_variables
from py_core.system.moderator import ModeratorSession
from py_core.utils.aac_corpus_downloader import AACCorpusDownloader
from chatlib.utils import env_helper
from nanoid import generate

if __name__ == "__main__":

    GlobalConfig.is_cli_mode = True


    env_file = find_dotenv()
    if not path.exists(env_file):
        env_file = open(path.join(getcwd(), '.env'), 'w')
        env_file.close()
        env_file = find_dotenv()

    #Supporting Korean    
    env_support_korean = env_helper.get_env_variable(env_variables.SUPPORT_KOREAN) or 'true'
    env_support_korean = env_support_korean.lower() == 'true'
    use_korean = questionary.confirm("Support the Korean language? ()", default = env_support_korean).ask()
    set_key(env_file, env_variables.SUPPORT_KOREAN, str(use_korean).lower())

    #Updating Card Translations
    if use_korean is True:
        env_auto_update_card_translations = env_helper.get_env_variable(core_env_variables.AUTO_UPDATE_CARD_TRANSLATIONS) or "false"
        env_auto_update_card_translations = env_auto_update_card_translations.lower() == 'true'
        auto_update_card_translations = questionary.confirm("Automatically update the global card translation dictionary?", default = env_auto_update_card_translations).ask()
        set_key(env_file, core_env_variables.AUTO_UPDATE_CARD_TRANSLATIONS, str(auto_update_card_translations).lower())

    ModeratorSession.assert_authorize(use_korean)

    if env_helper.get_env_variable(env_variables.AUTH_SECRET) is None:
        auth_secret = questionary.text("Insert auth secret (Any random string):", default="Naver1784", validate=make_non_empty_string_validator("Put a string with length > 0.")).ask()
        set_key(env_file, env_variables.AUTH_SECRET, auth_secret)

    if env_helper.get_env_variable(env_variables.ADMIN_HASHED_PASSWORD) is None:
        password: str = questionary.password("Insert admin password:", validate=lambda text: True if len(text) > 6 else "The password should be longer than 6 characters.").ask()
        import bcrypt
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        set_key(env_file, env_variables.ADMIN_HASHED_PASSWORD, hashed)
        set_key(env_file, env_variables.ADMIN_ID, generate('abcdefghijklmnopqrstuvwxyz01234567890', size=20))

    AACCorpusDownloader.download_corpus_cli()

    print("Setup complete.")
