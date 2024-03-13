"""Hello unit test module."""
import pytest
from py_core.hello import hello
from py_core.system.processor import ChildCardRecommendationGenerator

def test_hello():
    """Test the hello function."""
    assert hello() == "Hello aacesstalk-backend"


@pytest.mark.asyncio
async def test_processor():
    child_card_recommender = ChildCardRecommendationGenerator()

    card_recommendation_result = await child_card_recommender.generate()

    print(card_recommendation_result)


print(hello())
