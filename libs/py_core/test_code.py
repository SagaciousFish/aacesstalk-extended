from chatlib.global_config import GlobalConfig
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI

from py_core.system.processor import ChildCardRecommendationGenerator

import asyncio

async def test_processor():

    child_card_recommender = ChildCardRecommendationGenerator()

    card_recommendation_result = await child_card_recommender.generate()

    print(card_recommendation_result)


GlobalConfig.is_cli_mode = True
GPTChatCompletionAPI.assert_authorize()
asyncio.run(test_processor())
