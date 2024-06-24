from chatlib.tool.converter import generate_pydantic_converter
from pydantic import BaseModel, ConfigDict
from time import perf_counter

from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams

from py_core.config import AACessTalkConfig
from py_core.system.model import Dialogue, CardInfo, ChildCardRecommendationResult, ParentType, id_generator, CardCategory
from py_core.system.session_topic import SessionTopicInfo
from py_core.system.task.card_recommendation.common import ChildCardRecommendationAPIResult
from py_core.system.task.card_recommendation.translator import CardTranslator
from py_core.system.task.dialogue_conversion import DialogueInput, DialogueInputToStrConversionFunction
from py_core.utils.default_cards import DEFAULT_CORE_CARDS, DEFAULT_EMOTION_CARDS
from py_core.utils.vector_db import VectorDB

str_output_converter, output_str_converter = generate_pydantic_converter(ChildCardRecommendationAPIResult, 'yaml')

class ChildCardRecommendationParams(ChatCompletionFewShotMapperParams):
    model_config = ConfigDict(frozen=True)

    prev_recommendation: ChildCardRecommendationResult | None = None
    interim_cards: list[CardInfo] | None = None

_convert_input_to_str = DialogueInputToStrConversionFunction(include_topic=True)

class ChildCardRecommendationGenerator:

    def __init__(self, vector_db: VectorDB | None):
        api = GPTChatCompletionAPI()
        api.config().verbose = False

        self.__translator = CardTranslator(vector_db)

        def __prompt_generator(input: DialogueInput, params: ChildCardRecommendationParams) -> str:
            prompt = f"""
- You are a helpful assistant that serves as an Alternative Augmented Communication tool.
- Suppose that you are helping a communication with a child and a {input.parent_type.lower()}. The autistic child has the language proficiency of a 5 to 7-year-old, so recommendations should consider their cognitive level.
- For the conversation, {input.topic.to_readable_description()}
- Given the last message of the {input.parent_type.lower()}, suggest a list of English keywords that can help the child pick to create a sentence as an answer.
- Note that the 'core' cards are static and provided by default. So do NOT recommend the following cards: {", ".join([f"{c.get_label_for_parent(input.parent_type)}" for c in DEFAULT_CORE_CARDS])}
- Note that the 'emotion' cards must be selected from the given list: {", ".join([f"{c.get_label_for_parent(input.parent_type)}" for c in DEFAULT_EMOTION_CARDS])}
""""""

- Return an YAML string with variables as in the following:
    topics: [] // Noun topics that reflect detailed context based on your parents' questions
    actions: [] // Verb actions that can be matched with the suggested topics
    emotions: [] // Emotion candidates that may describe the feeling of the child. 
"""f"""

{"" if params.prev_recommendation is None else "- The child had previous recommendation: " + params.prev_recommendation.model_dump_json(exclude={"id", "timestamp"}) + ". Try to generate cards that are distinct to this previous recommendation."}
{"" if params.interim_cards is None else "- The child had selected the following cards: " + ', '.join([card.label for card in params.interim_cards]) + ". The generated recommendation should be relevant to these selections."}
- Provide 4 options for each category.
"""
            return prompt

        self.__mapper: ChatCompletionFewShotMapper[
            DialogueInput, ChildCardRecommendationAPIResult, ChildCardRecommendationParams] = (
            ChatCompletionFewShotMapper(api,
                                        instruction_generator=__prompt_generator,
                                        input_str_converter=_convert_input_to_str,
                                        output_str_converter=output_str_converter,
                                        str_output_converter=str_output_converter
                                        ))

    async def generate(self,
                       turn_id: str,
                       parent_type: ParentType,
                       topic_info: SessionTopicInfo,
                       dialogue: Dialogue,
                       interim_cards: list[CardInfo] | None = None,
                       previous_recommendation: ChildCardRecommendationResult | None = None,
                       ) -> ChildCardRecommendationResult:
        t_start = perf_counter()

        recommendation = await self.__mapper.run(None,
                                                 input=DialogueInput(dialogue=dialogue, topic=topic_info, parent_type=parent_type),
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
            (word, CardCategory.Action) for word in recommendation.actions]
        
        selected_emotion_cards = []
        for emotion in recommendation.emotions:
            matched = [c for c in DEFAULT_EMOTION_CARDS if c.label.lower().strip() == emotion.lower().strip()]
            if len(matched) > 0:
                selected_emotion_cards.append(matched[0])
            else:
                print(f"Emotion not matched - {emotion}")

        return ChildCardRecommendationResult(id=rec_id, turn_id=turn_id, cards=[
            CardInfo(label=word, label_localized=translated_keywords[i], category=category,
                     recommendation_id=rec_id) for i, (word, category) in
            enumerate(keyword_category_list)] + [CardInfo(label=c.get_label_for_parent(parent_type), label_localized=c.get_label_localized_for_parent(parent_type), 
                                                          recommendation_id=rec_id, category=c.category
                                                          ) for c in (selected_emotion_cards + DEFAULT_CORE_CARDS)])
