from pydantic import BaseModel, ConfigDict, TypeAdapter

from py_core.config import AACessTalkConfig
import yaml

from py_core.system.guide_categories import ParentGuideCategory
from py_core.system.model import Dyad, ParentExampleMessage, ParentGuideElement, ParentGuideRecommendationResult, UserLocale
from py_core.system.session_topic import SessionTopicCategory, SessionTopicInfo


class StaticGuideInfo(BaseModel):

    model_config=ConfigDict(use_enum_values=True, frozen=True)

    key: str

    guide_category: ParentGuideCategory

    guide: str
    guide_localized: str

    example: str
    example_localized: str


_guide_dict_type_adapter = TypeAdapter(dict[str, list[StaticGuideInfo]])

class StaticGuideFactory:
    
    def __init__(self):
        with open(AACessTalkConfig.initial_parent_guides_path) as f:
            obj = yaml.safe_load(f)
            self.__guide_dict: dict[SessionTopicCategory, list[StaticGuideInfo]] = _guide_dict_type_adapter.validate_python(obj)
    
    def get_guide_recommendation(self, topic: SessionTopicInfo, dyad: Dyad, turn_id: str) -> ParentGuideRecommendationResult:
        guides = [ParentGuideElement.messaging_guide(
            category=guide_info.guide_category, 
            guide=guide_info.guide.format(subtopic=topic.subtopic, child_name=dyad.child_name),
            guide_localized= None if dyad.locale == UserLocale.English else guide_info.guide_localized.format(subtopic=topic.subtopic, child_name=dyad.child_name),
            is_generated=False,
            static_guide_key=guide_info.key) for guide_info in self.__guide_dict[topic.category]]
        return ParentGuideRecommendationResult(guides=guides, turn_id=turn_id)

         
    def get_example_message(self, topic: SessionTopicInfo, dyad: Dyad, guide: ParentGuideElement, recommendation_id: str) -> ParentExampleMessage:
        if guide.static_guide_key is not None:
            guide_info = [g for g in self.__guide_dict[topic.category] if g.key == guide.static_guide_key][0]
            return ParentExampleMessage(recommendation_id=recommendation_id, guide_id=guide.id, 
                                        message=guide_info.example.format(subtopic=topic.subtopic, child_name=dyad.child_name),
                                        message_localized= None if dyad.locale == UserLocale.English else guide_info.example_localized.format(subtopic=topic.subtopic, child_name=dyad.child_name))
        else:
            raise Exception("Only static guides with a static guide key can yield an example message.")