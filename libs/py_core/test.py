from chatlib.llm.integration.openai_api import GPTChatCompletionAPI

from libs.py_core.py_core.system.processor import ChildCardRecommendationGenerator


async def test_processor():

    GPTChatCompletionAPI.authorize()

    child_card_recommender = ChildCardRecommendationGenerator()

    card_recommendation_result = await child_card_recommender.generate()

    print(card_recommendation_result)

