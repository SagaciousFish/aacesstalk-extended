import asyncio
import questionary
from chatlib.global_config import GlobalConfig
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI
from chatlib.utils.cli import make_non_empty_string_validator

from py_core.system.model import CardInfo, CardCategory, ParentType
from py_core.system.storage.user.memory import OnMemoryUserStorage
from py_core.system.task.card_image_matching import CardImageMatcher


async def routine(matcher: CardImageMatcher):

    while True:
        keyword: str = await questionary.text("Insert card names in English.", "School, Student, Family", validate=make_non_empty_string_validator("Empty string is not allowed.")).ask_async()
        keyword_localized: str = await questionary.text("Insert card names in Koreab.", "학교, 학생, 가족", validate=make_non_empty_string_validator("Empty string is not allowed.")).ask_async()
        

        matches = await matcher.match_card_images([CardInfo(recommendation_id="", label=kw, label_localized=kwl, category=CardCategory.Topic) for kw, kwl in zip(keyword.split(","), keyword_localized.split(","))], parent_type=ParentType.Father)

        for m in matches:
            print(await matcher.get_card_image_filepath(m.type, m.image_id))


if __name__ == "__main__":

    print("Test card image retrieval.")
    
    GlobalConfig.is_cli_mode = True
    GPTChatCompletionAPI.assert_authorize()

    user_storage = OnMemoryUserStorage(user_id=None)

    retriever = CardImageMatcher(user_storage)

    asyncio.run(routine(retriever))