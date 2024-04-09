from chatlib.global_config import GlobalConfig
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI

from py_core.system.task.card_recommendation.card_image_retriever import CardImageRetriever

GlobalConfig.is_cli_mode = True
GPTChatCompletionAPI.assert_authorize()

retriever = CardImageRetriever()

cards = retriever.query_nearest_card_image_infos("Climb / action")

print(cards)
