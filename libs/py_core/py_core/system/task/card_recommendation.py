from chatlib.llm.integration.openai_api import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.converter import generate_pydantic_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams
from pydantic import ConfigDict, BaseModel

from py_core.system.model import ChildCardRecommendationResult, Dialogue, CardInfo, \
    id_generator
from py_core.system.task.stringify import convert_dialogue_to_str


class ChildCardRecommendationAPIResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    nouns: list[str]
    emotions: list[str]
    actions: list[str]


str_output_converter, output_str_converter = generate_pydantic_converter(ChildCardRecommendationAPIResult, 'yaml')


class ChildCardRecommendationParams(ChatCompletionFewShotMapperParams):
    model_config = ConfigDict(frozen=True)

    prev_recommendation: ChildCardRecommendationResult | None = None
    interim_cards: list[CardInfo] | None = None


class ChildCardRecommendationGenerator:

    def __init__(self):

        api = GPTChatCompletionAPI()
        api.config().verbose = True

        self.__mapper: ChatCompletionFewShotMapper[Dialogue, ChildCardRecommendationAPIResult, ChildCardRecommendationParams] = (
            ChatCompletionFewShotMapper(api,
                                        instruction_generator=self.__prompt_generator,
                                        input_str_converter=convert_dialogue_to_str,
                                        output_str_converter=output_str_converter,
                                        str_output_converter=str_output_converter
                                        ))

    @staticmethod
    def __prompt_generator(input: Dialogue, params: ChildCardRecommendationParams) -> str:
        prompt = """
- You are a helpful assistant that serves as an Alternative Augmented Communication tool.
- Suppose that you are helping a communication with a child and parents in Korean. The autistic child has the language proficiency of a 6 to 8-year-old in Korean, so recommendations should consider their cognitive level.
- Given the last message of the parents, suggest a list of keywords that can help the child pick to create a sentence as an answer.
- Use honorific form of Korean for actions and emotions, such as "~해요" or "~어요", if possible.

Return an YAML string with variables as in the following:
nouns: [] // list of nouns that reflect detailed context based on your parents' questions.
actions: [] // Actions that can be matched with the nouns suggested in [nouns].
emotions: [] // Emotions that the child might want to express in the situation, including both positive and negative emotions and needs.
"""f"""

{"" if params.prev_recommendation is None else "- The child had previous recommendation: " + params.prev_recommendation.json(exclude=["id", "timestamp"]) + ". Try to generate phrases that are distinct to this previous recommendation."}
{"" if params.interim_cards is None else "- The child had selected the following cards: " + ', '.join([card.text for card in params.interim_cards]) + ". The generated recommendation should be relevant to these selections."}
- Provide up to five options for each category.
"""
        return prompt

    async def generate(self,
                       dialogue: Dialogue,
                       interim_cards: list[CardInfo] | None = None,
                       previous_recommendation: ChildCardRecommendationResult | None = None) -> ChildCardRecommendationResult:
        recommendation = await self.__mapper.run(None,
                                       input=dialogue,
                                       params=ChildCardRecommendationParams(prev_recommendation=previous_recommendation,
                                                                            interim_cards=interim_cards,
                                                                            model=ChatGPTModel.GPT_4_0613,
                                                                            api_params={}))

        rec_id = id_generator()
        return ChildCardRecommendationResult(id=rec_id, cards=[CardInfo(text=noun, category='noun', recommendation_id=rec_id) for noun in recommendation.nouns] + \
               [CardInfo(text=emotion, category='emotion', recommendation_id=rec_id) for emotion in recommendation.emotions] + \
               [CardInfo(text=action, category='action', recommendation_id=rec_id) for action in recommendation.actions])
