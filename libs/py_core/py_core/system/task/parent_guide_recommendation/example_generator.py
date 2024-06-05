from time import perf_counter

from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.converter import str_to_str_noop
from chatlib.utils.jinja_utils import convert_to_jinja_template
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapperParams, ChatCompletionFewShotMapper, \
    MapperInputOutputPair
from pydantic import BaseModel

from py_core.system.guide_categories import ParentGuideCategory
from py_core.system.model import ParentGuideElement, ParentExampleMessage, Dialogue, DialogueMessage, CardCategory
from py_core.system.task.parent_guide_recommendation.example_translator import ParentExampleMessageTranslator
from py_core.system.task.card_recommendation.common import DialogueToStrConversionFunction
from py_core.utils.vector_db import VectorDB


class ParentExampleMessageGenerationInput(BaseModel):
    dialogue: Dialogue
    guide: ParentGuideElement


_dialogue_to_str = DialogueToStrConversionFunction()


def _convert_input_to_str(input: ParentExampleMessageGenerationInput, params) -> str:
    return f"""{_dialogue_to_str(input.dialogue, params)}
    <message_generation_guide>{input.guide.guide}</message_generation_guide>
    """


_PROMPT = """You are a helpful assistant who helps facilitate communication between minimally verbal autistic children and their parents. The goal of their conversation is to help the child and parent elaborate on a topic together.
[Task] Given a dialogue between a parent and a child and a message generation guide, suggest an example utterance that the parent can respond to the child's last message.

[Input]
<dialogue/>: The current state of the conversation
<message_generation_guide/>: A guidance for example utterance generation

[Output]
A text string containing an utterance of the parent that complies with the message generation guide.
Output should consist of a single sentence at most, and should be short, within 8 words.
"""

_EXAMPLES = [
    MapperInputOutputPair(
        input=ParentExampleMessageGenerationInput(
            dialogue=[
                DialogueMessage.example_parent_message("Did you remember that we will visit granma today?"),
                DialogueMessage.example_child_message(("Grandma", CardCategory.Topic), ("Play", CardCategory.Action))
            ],
            guide=ParentGuideElement.messaging_guide(ParentGuideCategory.Encourage,
                                                     "Suggest things that the kid can do with grandma playing.")
        ),
        output="What do you want to play with granma? You may go picnic with her or play with toys."
    ),
    MapperInputOutputPair(
        input=ParentExampleMessageGenerationInput(
            dialogue=[
                DialogueMessage.example_parent_message("How was your day at kinder?"),
                DialogueMessage.example_child_message(
                    ("Kinder", CardCategory.Topic),
                    ("Friend", CardCategory.Topic),
                    ("Tough", CardCategory.Emotion)),
            ],
            guide=ParentGuideElement.messaging_guide(ParentGuideCategory.Empathize,
                                                     "Empathize that the kid had tough time due to a friend.")
        ),
        output="That must be tough due to a friend!"
    )
]


class ParentExampleMessageGenerator:
    def __init__(self, vector_db: VectorDB | None):
        api = GPTChatCompletionAPI()
        api.config().verbose = False

        self.__mapper: ChatCompletionFewShotMapper[
            ParentExampleMessageGenerationInput,
            str,
            ChatCompletionFewShotMapperParams] = ChatCompletionFewShotMapper(
            api,
            instruction_generator=_PROMPT,
            input_str_converter=_convert_input_to_str,
            output_str_converter=str_to_str_noop,
            str_output_converter=str_to_str_noop
        )

        self.__translator = ParentExampleMessageTranslator(vector_db)

    async def generate(self, dialogue: Dialogue, guide: ParentGuideElement,
                       recommendation_id: str) -> ParentExampleMessage:
        t_start = perf_counter()
        utterance = await self.__mapper.run(_EXAMPLES,
                                            ParentExampleMessageGenerationInput(dialogue=dialogue, guide=guide),
                                            ChatCompletionFewShotMapperParams(model=ChatGPTModel.GPT_4_0613,
                                                                              api_params={}))
        translated_utterance = await self.__translator.translate_example(utterance)
        t_end = perf_counter()
        # print(f"Example generation took {t_end - t_start} sec - {utterance} ({guide.category} - {guide.guide})")

        return ParentExampleMessage(recommendation_id=recommendation_id, guide_id=guide.id, message=utterance,
                                    message_localized=translated_utterance)
