

from pydantic import BaseModel
import yaml

from py_core.config import AACessTalkConfig
from os import path
from py_core.system.model import CardCategory, ChildGender, ParentType


class DefaultCardInfo(BaseModel):
    id: str
    label: str | dict[ParentType, str]
    label_localized: str | dict[ParentType, str]
    category: CardCategory
    image: None | str | dict[ParentType | ChildGender, str] = None

    def get_label_for_parent(self, parent_type: ParentType)->str:
        if isinstance(self.label, str):
            return self.label
        else:
            return self.label[parent_type]
    
    def get_label_localized_for_parent(self, parent_type: ParentType)->str:
        if isinstance(self.label_localized, str):
            return self.label_localized
        else:
            return self.label_localized[parent_type]
        
    def get_image_path_for_dyad(self, parent_type: ParentType, child_gender: ChildGender)->str | None:
        if self.image is not None:
            if isinstance(self.image, str):
                return self.image
            else:
                return self.image[parent_type] if parent_type in self.image else self.image[child_gender]
        else:
            return None
    
    def get_all_image_paths(self) -> list[str]:
        if self.image is not None:
            if isinstance(self.image, str):
                return [self.image]
            else:
                return [v for k,v in self.image.items()]
        else:
            return []


def load_default_cards(path: str)->list[DefaultCardInfo]:
    with open(path) as f:
       l = yaml.load(f, yaml.SafeLoader)
       return [DefaultCardInfo(**e) for e in l]
    
DEFAULT_EMOTION_CARDS = load_default_cards(AACessTalkConfig.default_emotion_card_table_path)
DEFAULT_EMOTION_LABELS = [c.label.lower().strip() for c in DEFAULT_EMOTION_CARDS]

DEFAULT_CORE_CARDS = load_default_cards(AACessTalkConfig.default_core_card_table_path)

DEFAULT_CARDS = DEFAULT_EMOTION_CARDS + DEFAULT_CORE_CARDS

DEFAULT_CARDS_BY_ID: dict[str, DefaultCardInfo] = {c.id:c for c in DEFAULT_CARDS}

def find_default_card(label_localized: str, category: CardCategory, parent_type: ParentType) -> DefaultCardInfo | None:
    filtered = [c for c in DEFAULT_CARDS if c.category == category and c.get_label_localized_for_parent(parent_type=parent_type) == label_localized]
    if len(filtered) > 0:
        return filtered[0]
    else:
        return None
    
def find_default_card_by_id(id: str) -> DefaultCardInfo:
    return DEFAULT_CARDS_BY_ID[id]

# Inspect default card images
for card in DEFAULT_CARDS:
    for image_path in card.get_all_image_paths():
        abs_path = path.join(AACessTalkConfig.card_image_directory_path, image_path)

        print(abs_path)
        
        assert path.exists(abs_path), f"Default card image does not exists at {abs_path} : {card.label_localized}"