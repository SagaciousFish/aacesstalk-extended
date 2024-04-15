import questionary
from chatlib.global_config import GlobalConfig
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI
from chatlib.utils.cli import make_non_empty_string_validator

from py_core.system.task.card_recommendation.card_image_retriever import CardImageRetriever


if __name__ == "__main__":

    GlobalConfig.is_cli_mode = True
    GPTChatCompletionAPI.assert_authorize()

    retriever = CardImageRetriever()

    while True:
        keyword = questionary.text("Insert card name in English.", "School", validate=make_non_empty_string_validator("Empty string is not allowed.")).ask()
        cards = retriever.query_nearest_card_image_infos(keyword, k=1)
        print(cards)
