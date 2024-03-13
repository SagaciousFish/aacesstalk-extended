from typing import Any

from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams
from chatlib.tool.converter import generate_pydantic_converter
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI, ChatGPTModel

from libs.py_core.py_core.system.model import ChildCardRecommendationResult, Dialogue, DialogueMessage, DialogueRole


class ChildCardRecommendationGenerator:

    def __init__(self):
        str_output_converter, output_str_converter = generate_pydantic_converter(ChildCardRecommendationResult)

        self.__mapper: ChatCompletionFewShotMapper[Dialogue, ChildCardRecommendationResult, Any] = (
            ChatCompletionFewShotMapper(GPTChatCompletionAPI(),
                                        instruction_generator=f"""
                                        You are a helpful assistant that serves as an Alternative Augmented Communication tool.
Suppose that you are helping a communication with a child and parents in Korean. The autistic child has the language proficiency of a 6 to 8-year-old in Korean, so recommendations should consider their cognitive level.
Given the last message of the parents, suggest a list of keywords that can help the child pick to create a sentence as an answer.
Proceed in the following order.
1. [nouns] : Provide nouns that reflect detailed context based on your parents' questions.
2. [actions] : Provide words for the action that can be matched with the nouns suggested in [nouns].
3. [emotions] : Suggest emotions that the child might want to express in the situation, including both positive and negative emotions and needs.
Note that the output must be JSON, formatted like the following:
{ChildCardRecommendationResult.schema_json()}
The result should be in Korean and please provide up to four options for each element.
                                        """,
                                        input_str_converter=lambda dialogue, params: dialogue.json(),
                                        output_str_converter=output_str_converter,
                                        str_output_converter=str_output_converter
                                        ))

    async def generate(self) -> ChildCardRecommendationResult:
        return await self.__mapper.run(None, input=[DialogueMessage(speaker=DialogueRole.Parent, content="오늘 학교에서 뭐 했어?")],
                                       params=ChatCompletionFewShotMapperParams(model = ChatGPTModel.GPT_4_0125, api_params={}))

