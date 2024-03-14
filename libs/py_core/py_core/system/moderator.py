from py_core.system.model import ChildCardRecommendationResult, Dialogue, DialogueMessage, DialogueRole, CardInfo
from py_core.system.task import ChildCardRecommendationGenerator

class Moderator:

    def __init__(self):
        self.child_card_recommender = ChildCardRecommendationGenerator()

    async def start_new_session(self, parent_message: str) -> tuple[ChildCardRecommendationResult, Dialogue]:
        dialogue = [DialogueMessage(speaker=DialogueRole.Parent,
                                    content=parent_message)]
        recommendation = await self.child_card_recommender.generate(dialogue, None)
        return recommendation, dialogue

    async def refresh_child_card_recommendation(self, dialogue: Dialogue,
                                                interim_cards: list[CardInfo],
                                                prev_recommendation: ChildCardRecommendationResult) -> tuple[ChildCardRecommendationResult, Dialogue]:
        recommendation = await self.child_card_recommender.generate(dialogue, interim_cards, prev_recommendation)
        return recommendation, dialogue

    async def submit_child_selected_card(self, dialogue: Dialogue, selected_cards: list[CardInfo]) -> None:
        pass
