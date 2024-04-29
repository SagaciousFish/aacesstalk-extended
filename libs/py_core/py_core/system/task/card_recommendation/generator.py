from chatlib.tool.converter import generate_pydantic_converter
from pydantic import ConfigDict
from time import perf_counter

from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams

from py_core.system.model import Dialogue, CardInfo, ChildCardRecommendationResult, id_generator, CardCategory
from py_core.system.task.card_recommendation.common import ChildCardRecommendationAPIResult
from py_core.system.task.card_recommendation.translator import CardTranslator
from py_core.system.task.stringify import DialogueToStrConversionFunction
from py_core.utils.vector_db import VectorDB

str_output_converter, output_str_converter = generate_pydantic_converter(ChildCardRecommendationAPIResult, 'yaml')


class ChildCardRecommendationParams(ChatCompletionFewShotMapperParams):
    model_config = ConfigDict(frozen=True)

    prev_recommendation: ChildCardRecommendationResult | None = None
    interim_cards: list[CardInfo] | None = None


class ChildCardRecommendationGenerator:

    def __init__(self, vector_db: VectorDB | None):
        api = GPTChatCompletionAPI()
        api.config().verbose = False

        self.__mapper: ChatCompletionFewShotMapper[
            Dialogue, ChildCardRecommendationAPIResult, ChildCardRecommendationParams] = (
            ChatCompletionFewShotMapper(api,
                                        instruction_generator=self.__prompt_generator,
                                        input_str_converter=DialogueToStrConversionFunction(),
                                        output_str_converter=output_str_converter,
                                        str_output_converter=str_output_converter
                                        ))

        self.__translator = CardTranslator(vector_db)

    @staticmethod
    def __prompt_generator(input: Dialogue, params: ChildCardRecommendationParams) -> str:
        prompt = """
- You are a helpful assistant that serves as an Alternative Augmented Communication tool.
- Suppose that you are helping a communication with a child and parents in Korean. The autistic child has the language proficiency of a 5 to 7-year-old, so recommendations should consider their cognitive level.
- Given the last message of the parents, suggest a list of English keywords that can help the child pick to create a sentence as an answer.

Return an YAML string with variables as in the following:
topics: [] // Noun topics that reflect detailed context based on your parents' questions
actions: [] // Verb actions that can be matched with the suggested topics
emotions: [] // Adjective or adverb Emotions that the child might want to express in the situation, including both positive and negative emotions and needs
"""f"""

{"" if params.prev_recommendation is None else "- The child had previous recommendation: " + params.prev_recommendation.json(exclude={"id", "timestamp"}) + ". Try to generate phrases that are distinct to this previous recommendation."}
{"" if params.interim_cards is None else "- The child had selected the following cards: " + ', '.join([card.label for card in params.interim_cards]) + ". The generated recommendation should be relevant to these selections."}
- Provide up to five options for each category.
"""
        return prompt

    async def generate(self,
                       dialogue: Dialogue,
                       interim_cards: list[CardInfo] | None = None,
                       previous_recommendation: ChildCardRecommendationResult | None = None) -> ChildCardRecommendationResult:
        t_start = perf_counter()

        recommendation = await self.__mapper.run(None,
                                                 input=dialogue,
                                                 params=ChildCardRecommendationParams(
                                                     prev_recommendation=previous_recommendation,
                                                     interim_cards=interim_cards,
                                                     model=ChatGPTModel.GPT_4_0613,
                                                     api_params={}))

        t_trans = perf_counter()

        print(f"English cards generated: {t_trans - t_start} sec.")

        translated_keywords = await self.__translator.translate(recommendation)

        t_end = perf_counter()

        print(f"Card translated {t_end - t_trans} sec.")
        print(f"Total latency: {t_end - t_start} sec.")

        rec_id = id_generator()

        keyword_category_list = [(word, CardCategory.Topic) for word in recommendation.topics] + [
            (word, CardCategory.Action) for word in recommendation.actions] + [(word, CardCategory.Emotion) for word in
                                                                               recommendation.emotions]

        return ChildCardRecommendationResult(id=rec_id, cards=[
            CardInfo(label=word, label_localized=translated_keywords[i], category=category,
                     recommendation_id=rec_id) for i, (word, category) in
            enumerate(keyword_category_list)])
