import json
from enum import StrEnum
from typing import Any
from pydantic import ConfigDict

from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams
from chatlib.tool.converter import generate_pydantic_converter
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI, ChatGPTModel

from py_core.system.model import ChildCardRecommendationResult, Dialogue, DialogueMessage, DialogueRole, CardInfo
from py_core.system.task.stringify import convert_dialogue_to_str

str_output_converter, output_str_converter = generate_pydantic_converter(ChildCardRecommendationResult)


class ChildCardRecommendationParams(ChatCompletionFewShotMapperParams):
    model_config = ConfigDict(frozen=True)

    prev_recommendation: ChildCardRecommendationResult | None = None
    interim_cards: list[CardInfo] | None = None


class ChildCardRecommendationGenerator:

    def __init__(self):
        self.__mapper: ChatCompletionFewShotMapper[Dialogue, ChildCardRecommendationResult, ChildCardRecommendationParams] = (
            ChatCompletionFewShotMapper(GPTChatCompletionAPI(),
                                        instruction_generator=self.__prompt_generator,
                                        input_str_converter=convert_dialogue_to_str,
                                        output_str_converter=output_str_converter,
                                        str_output_converter=str_output_converter
                                        ))

    @staticmethod
    def __prompt_generator(input: Dialogue, params: ChildCardRecommendationParams) -> str:
        prompt = f"""
- You are a helpful assistant that serves as an Alternative Augmented Communication tool.
- Suppose that you are helping a communication with a child and parents in Korean. The autistic child has the language proficiency of a 6 to 8-year-old in Korean, so recommendations should consider their cognitive level.
- Given the last message of the parents, suggest a list of keywords that can help the child pick to create a sentence as an answer.
- Use honorific form of Korean for actions and emotions, such as "~해요" or "~어요", if possible.

Proceed in the following order.
1. [nouns] : Provide nouns that reflect detailed context based on your parents' questions.
2. [actions] : Provide words for the action that can be matched with the nouns suggested in [nouns].
3. [emotions] : Suggest emotions that the child might want to express in the situation, including both positive and negative emotions and needs.

{"" if params.prev_recommendation is None else "- The child had previous recommendation: " + params.prev_recommendation.json() + ". Try to generate phrases that are distinct to this previous recommendation."}
{"" if params.interim_cards is None else "- The child had selected the following cards: " + ', '.join([card.simple_str() for card in params.interim_cards]) + ". The generated recommendation should be relevant to these selections."}

Note that the output must be JSON, formatted like the following:

  "nouns": Array<string>
  "actions: Array<string>
  "emotions": Array<string>

The result should be in Korean and please provide up to four options for each element.
"""
        return prompt

    async def generate(self,
                       dialogue: Dialogue,
                       interim_cards: list[CardInfo] | None = None,
                       previous_recommendation: ChildCardRecommendationResult | None = None) -> ChildCardRecommendationResult:
        return await self.__mapper.run(None,
                                       input=dialogue,
                                       params=ChildCardRecommendationParams(prev_recommendation=previous_recommendation,
                                                                            interim_cards=interim_cards,
                                                                            model=ChatGPTModel.GPT_4_0613,
                                                                            api_params={}))
