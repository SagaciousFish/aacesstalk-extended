from time import perf_counter

from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.converter import str_to_str_noop
from chatlib.utils.jinja_utils import convert_to_jinja_template
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapperParams, ChatCompletionFewShotMapper
from pydantic import BaseModel

from py_core.system.model import ParentGuideElement, ParentExampleMessage, Dialogue
from py_core.system.task.parent_guide_recommendation.example_translator import ParentExampleMessageTranslator
from py_core.system.task.stringify import DialogueToStrConversionFunction


class ParentExampleMessageGenerationInput(BaseModel):
    dialogue: Dialogue
    guide: ParentGuideElement

_dialogue_to_str = DialogueToStrConversionFunction()

def _convert_input_to_str(input: ParentExampleMessageGenerationInput, params)->str:
    return f"""{_dialogue_to_str(input.dialogue, params)}
    <message_generation_guide>{input.guide.guide}</message_generation_guide>
    """


_prompt_template = convert_to_jinja_template("""
You are a helpful assistant who helps facilitate communication between minimally verbal autistic children and their parents. The goal of their conversation is to help the child and parent elaborate on a topic together.
[Task] Given a dialogue between a parent and a child and a message generation guide, suggest an example utterance that the parent can respond to the child's last message.

[Input]
<dialogue/>: The current state of the conversation
<message_generation_guide/>: A guidance for example utterance generation

[Output]
A text string containing an utterance of the parent that complies with the message generation guide.
""")

def _prompt_generator(input: ParentExampleMessageGenerationInput, params) -> str:
    return _prompt_template.render()

class ParentExampleMessageGenerator:
    def __init__(self):
        api = GPTChatCompletionAPI()
        api.config().verbose = False

        self.__mapper: ChatCompletionFewShotMapper[
            ParentExampleMessageGenerationInput,
            str,
            ChatCompletionFewShotMapperParams] = ChatCompletionFewShotMapper(
            api,
            instruction_generator=_prompt_generator,
            input_str_converter=_convert_input_to_str,
            output_str_converter=str_to_str_noop,
            str_output_converter=str_to_str_noop
        )

        self.__translator = ParentExampleMessageTranslator()

    async def generate(self, dialogue: Dialogue, guide: ParentGuideElement, recommendation_id: str) -> ParentExampleMessage:

        t_start = perf_counter()
        utterance = await self.__mapper.run(None, ParentExampleMessageGenerationInput(dialogue=dialogue, guide=guide),
                                            ChatCompletionFewShotMapperParams(model=ChatGPTModel.GPT_4_0613, api_params={}))
        translated_utterance = await self.__translator.translate_example(utterance)
        t_end = perf_counter()
        # print(f"Example generation took {t_end - t_start} sec - {utterance} ({guide.category} - {guide.guide})")

        return ParentExampleMessage(recommendation_id=recommendation_id, guide_id=guide.id, message=utterance, message_localized=translated_utterance)
