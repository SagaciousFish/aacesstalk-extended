from py_core.system.model import CardCategory, FreeTopicDetail, UserDefinedCardInfo
from py_core.system.storage import UserStorage


class OnMemoryUserStorage(UserStorage):

    def __init__(self, user_id: str | None):
        super().__init__(user_id)
        self.__user_defined_cards: dict[(str, str), list[UserDefinedCardInfo]] = {}
        self.__user_defined_cards_by_id: dict[str, UserDefinedCardInfo] = {}
        self.__free_topic_details: dict[str, FreeTopicDetail] = {}

    async def register_user_defined_card(self, info: UserDefinedCardInfo):
        if info.id not in self.__user_defined_cards_by_id:
            self.__user_defined_cards_by_id[info.id] = info

            key = (info.category, info.label)
            if key in self.__user_defined_cards and self.__user_defined_cards[key] is not None:
                l = self.__user_defined_cards[key]
                l.append(info)
                l.sort(key=lambda i: i.timestamp, reverse=False)
            else:
                self.__user_defined_cards[key] = [info]

    async def get_user_defined_cards(self) -> list[UserDefinedCardInfo]:
        return [v[len(v) - 1] for k, v in self.__user_defined_cards.items() if v is not None and len(v) >= 1]

    async def query_user_defined_card(self, category: CardCategory, label_localized: str) -> UserDefinedCardInfo | None:
        if (category, label_localized) in self.__user_defined_cards:
            infos = self.__user_defined_cards[(category, label_localized)]
            return infos[len(infos) - 1]
        else:
            return None

    async def get_user_defined_card(self, id: str) -> UserDefinedCardInfo | None:
        return self.__user_defined_cards_by_id[id]

    async def upsert_free_topic_detail(self, detail: FreeTopicDetail):
        self.__free_topic_details[detail.id] = detail

    async def get_free_topic_details(self) -> list[FreeTopicDetail]:
        return [elm for id, elm in self.__free_topic_details.items()]

    async def remove_free_topic_detail(self, id: str):
        self.__free_topic_details[id] = None

    async def get_free_topic_detail(self, id: str) -> FreeTopicDetail | None:
        return self.__free_topic_details[id] if id in self.__free_topic_details else None

    async def remove_user_defined_card(self, id: str):
        self.__user_defined_cards_by_id[id] = None
        