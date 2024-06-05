from chatlib.llm.integration.openai_api import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.converter import generate_pydantic_list_converter
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams, \
    MapperInputOutputPair
from chatlib.utils.jinja_utils import convert_to_jinja_template
from time import perf_counter

from py_core.system.guide_categories import ParentGuideCategory
from py_core.system.model import CardCategory, DialogueMessage, ParentGuideRecommendationResult, Dialogue, ParentGuideElement, ParentType, Dyad
from py_core.system.task.parent_guide_recommendation.common import ParentGuideRecommendationAPIResult, \
    DialogueInspectionResult
from py_core.system.task.parent_guide_recommendation.guide_translator import GuideTranslator
from py_core.system.task.common import DialogueInput, DialogueInputToStrConversionFunction
from py_core.system.session_topic import SessionTopicCategory, SessionTopicInfo

class ParentGuideRecommendationParams(ChatCompletionFewShotMapperParams):
    dialogue_inspection_result: DialogueInspectionResult | None = None

    @classmethod
    def instance(cls, dialogue_inspection_result: DialogueInspectionResult | None = None) -> 'ParentGuideRecommendationParams':
        return cls(model=ChatGPTModel.GPT_4_0613, api_params={}, dialogue_inspection_result=dialogue_inspection_result)

_convert_input_to_str = DialogueInputToStrConversionFunction(include_topic=True, include_parent_type=True)


# Variables for mapper ================================================================================================================

_prompt_template = convert_to_jinja_template("""
- Role: You are a helpful assistant who helps facilitate communication between minimally verbal autistic children and their parents.
- Goal of the conversation: {{topic_description}} Help the child and the {{parent_type}} elaborate on that topic together.
{%- if dialogue | length > 0 %}
- Task: Given a dialogue between a {{parent_type}} and a child, suggest a list of guides that can help the {{parent_type}} choose how to respond or ask questions in response to the child's last message. Note that the child always conveys their message through keywords.
{%else%}
- Task: With regards to the goal of conversation, suggest a list of guides that can help the {{parent_type}} as starting points of conversation.                                           
{%endif%}
                

[General instructions for parent's guide]
- Provide simple and easy-to-understand sentences consisting of no more than 5-6 words.
- Each guide should contain one purpose or intention.
- {%if dialogue | length > 0 -%}Based on the child's last message, s{%else%}S{%endif%}elect up to {% if dialogue_inspection_result is not none and dialogue_inspection_result.feedback is not none %}2{% else %}3{% endif %} most appropriate directions from the parent guide categories provided below.
{% if dialogue | length > 0 %}- Each guide should be contextualized based on the child's response and not be too general.{%endif%}

[Parent guide categories]
{%- for category in categories -%}
{%- if (category.min_turns is none) or (category.min_turns <= (dialogue | length)) %}
- "{{category.label}}": {{category.description}}.
{%- endif -%}
{%- endfor %}

[Response format]
Return a json list with each element formatted as:
{
  "category": The category of "Parent guide category",
  "guide": The guide message provided to the {{parent_type}}.
}

""")

def generate_parent_guideline_prompt(input: DialogueInput, params: ParentGuideRecommendationParams) -> str:
    
    prompt = _prompt_template.render(
        dialogue_inspection_result=params.dialogue_inspection_result, 
        dialogue=input.dialogue, 
        categories=ParentGuideCategory.values_with_desc(),
        topic_description=input.topic.to_readable_description(),
        parent_type=input.parent_type
    )
    return prompt


PARENT_GUIDE_EXAMPLES: list[MapperInputOutputPair[DialogueInput, ParentGuideRecommendationAPIResult]] = [
    MapperInputOutputPair(
        input=DialogueInput(topic=SessionTopicInfo(category=SessionTopicCategory.Plan), parent_type=ParentType.Mother, dialogue=[
            DialogueMessage.example_parent_message("Did you remember that we will visit granma today?"),
            DialogueMessage.example_child_message(("Grandma", CardCategory.Topic), ("Play", CardCategory.Action))
        ]),
        output=[
            ParentGuideElement.messaging_guide(ParentGuideCategory.Empathize, "Repeat that your kid wants to play with grandma."),
            ParentGuideElement.messaging_guide(ParentGuideCategory.Encourage, "Suggest things that the kid can do with grandma playing."),
            ParentGuideElement.messaging_guide(ParentGuideCategory.Specification, "Ask about what your kid wants to do playing."),
        ]
    ),
    MapperInputOutputPair(
        input=DialogueInput(topic=SessionTopicInfo(category=SessionTopicCategory.Recall), parent_type=ParentType.Father, dialogue=[
            DialogueMessage.example_parent_message("How was your day at kinder?"),
            DialogueMessage.example_child_message(
                ("Kinder", CardCategory.Topic),
                ("Friend", CardCategory.Topic),
                ("Tough", CardCategory.Emotion)),
        ]),
        output=[
            ParentGuideElement.messaging_guide(ParentGuideCategory.Empathize, "Empathize that the kid had tough time due to a friend."),
            ParentGuideElement.messaging_guide(ParentGuideCategory.Intention, "Check whether the kid had tough time with the friend."),
            ParentGuideElement.messaging_guide(ParentGuideCategory.Specification, "Ask what was tough with the friend."),
        ]
    )
]


# Generator ==========================================
class ParentGuideRecommendationGenerator:

    def __init__(self):
        str_output_converter, output_str_converter = generate_pydantic_list_converter(ParentGuideRecommendationAPIResult, ParentGuideElement, 'yaml', dict(include={"category", "guide"}))

        api = GPTChatCompletionAPI()
        api.config().verbose = False

        self.__mapper: ChatCompletionFewShotMapper[
            DialogueInput, ParentGuideRecommendationAPIResult, ParentGuideRecommendationParams] = ChatCompletionFewShotMapper(
            api,
            instruction_generator=generate_parent_guideline_prompt,
            input_str_converter=_convert_input_to_str,
            output_str_converter=output_str_converter,
            str_output_converter=str_output_converter
            )

        self.__translator = GuideTranslator()

    async def generate(self, dyad: Dyad, topic: SessionTopicInfo, dialogue: Dialogue, inspection_result: DialogueInspectionResult | None) -> ParentGuideRecommendationResult:
        t_start = perf_counter()

        parent_type_str = dyad.parent_type.value
        
        guide_list: ParentGuideRecommendationAPIResult = await self.__mapper.run(PARENT_GUIDE_EXAMPLES, DialogueInput(parent_type=parent_type_str, topic=topic, dialogue=dialogue),
                                                                                 ParentGuideRecommendationParams.instance(inspection_result))
        

        if inspection_result is not None and inspection_result.feedback is not None:
            guide_list = guide_list[:2]
            guide_list.insert(0, ParentGuideElement.feedback(inspection_result.categories, inspection_result.feedback))
        else:
            guide_list = guide_list[:3]

        print(guide_list)
        t_trans = perf_counter()
        print(f"Mapping took {t_trans - t_start} sec. Start translation...")
        translated_guide_list: ParentGuideRecommendationAPIResult = await self.__translator.translate(guide_list)
        t_end = perf_counter()
        print(f"Translation took {t_end - t_trans} sec.")
        print(f"Total latency: {t_end - t_start} sec.")
        return ParentGuideRecommendationResult(guides=translated_guide_list)
