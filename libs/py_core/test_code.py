from chatlib.global_config import GlobalConfig
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI

from py_core.system.model import ChildCardRecommendationResult, DialogueMessage, DialogueRole, CardInfo
from py_core.system.task import ChildCardRecommendationGenerator

import asyncio

from py_core.system.task.parent_guide_recommendation import ParentGuideRecommendationGenerator


async def test_processor():

    child_card_recommender = ChildCardRecommendationGenerator()

    card_recommendation_result = await child_card_recommender.generate([DialogueMessage(speaker=DialogueRole.Parent, content="할머니 댁 가는 거 알지? 할머니네 가면 뭐 하고 싶니?")],
                                                                       [CardInfo(text="물놀이", category="noun"), CardInfo(text="가고싶어요", category="noun")], None)

    print("==Child card recommendation=========")
    print(card_recommendation_result.model_dump_json(indent=2))

    parent_guide_recommender = ParentGuideRecommendationGenerator()

    parent_guide_recommendation = await parent_guide_recommender.generate([
        DialogueMessage(speaker=DialogueRole.Parent, content="할머니 댁 가는 거 알지? 할머니네 가면 뭐 하고 싶니?"),
        DialogueMessage(speaker=DialogueRole.Child, content=[CardInfo(text="수영", category="noun"), CardInfo(text="할아버지", category="noun")])
    ],)

    print("==Parent guide recommendation=========")
    print(parent_guide_recommendation.model_dump_json(indent=2))

GlobalConfig.is_cli_mode = True
GPTChatCompletionAPI.assert_authorize()
asyncio.run(test_processor())
