import json
from typing import Any

from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams
from chatlib.tool.converter import generate_pydantic_converter
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI, ChatGPTModel

from py_core.system.model import ChildCardRecommendationResult, Dialogue, DialogueMessage, DialogueRole

str_output_converter, output_str_converter = generate_pydantic_converter(ChildCardRecommendationResult)

def convert_dialogue_to_str(dialogue: Dialogue, params) -> str:
    script = "\n".join([f"<msg>{'Parent' if message.speaker == DialogueRole.Parent else 'Child'}: {message.content if isinstance(message.content, str) else ', '.join(message.content)}</msg>" for message in dialogue])

    result = f"""<dialogue>
    {script}
</dialogue>"""
    print(result)
    return result

class ChildCardRecommendationGenerator:

    def __init__(self):
        self.__mapper: ChatCompletionFewShotMapper[Dialogue, ChildCardRecommendationResult, Any] = (
            ChatCompletionFewShotMapper(GPTChatCompletionAPI(),
                                        instruction_generator="""
                                        You are a helpful assistant that serves as an Alternative Augmented Communication tool.
- Suppose that you are helping a communication with a child and parents in Korean. The autistic child has the language proficiency of a 6 to 8-year-old in Korean, so recommendations should consider their cognitive level.
- Given the last message of the parents, suggest a list of keywords that can help the child pick to create a sentence as an answer.
- Use honorific form of Korean for actions and emotions, such as "~해요" or "~어요", if possible.

Proceed in the following order.
1. [nouns] : Provide nouns that reflect detailed context based on your parents' questions.
2. [actions] : Provide words for the action that can be matched with the nouns suggested in [nouns].
3. [emotions] : Suggest emotions that the child might want to express in the situation, including both positive and negative emotions and needs.
Note that the output must be JSON, formatted like the following:
{
  "nouns": Array<string>
  "actions: Array<string>
  "emotions": Array<string>
}
The result should be in Korean and please provide up to four options for each element.
                                        """,
                                        input_str_converter=convert_dialogue_to_str,
                                        output_str_converter=output_str_converter,
                                        str_output_converter=str_output_converter
                                        ))

    async def generate(self) -> ChildCardRecommendationResult:
        return await self.__mapper.run(None,
                                       input=[
                                           DialogueMessage(speaker=DialogueRole.Parent, content="오늘 할머니네 가기로 한 거 알지? 너는 할머니랑 뭐 하고 싶어?")
                                       ],
                                       params=ChatCompletionFewShotMapperParams(model=ChatGPTModel.GPT_4_0613,
                                                                                api_params={}))
