import questionary
from chatlib.llm.chat_completion_api import make_non_empty_string_validator

from py_core import ModeratorSession
from py_core.system.model import ChildCardRecommendationResult, ParentGuideRecommendationResult, CardInfo, DialogueRole


async def test_session_loop(session: ModeratorSession):
    current_card_recommendation_result: ChildCardRecommendationResult | None = None
    current_parent_guide_recommendation_result: ParentGuideRecommendationResult | None = None
    current_interim_cards: list[CardInfo] = []

    while True:
        if session.next_speaker == DialogueRole.Parent:

            if current_parent_guide_recommendation_result is not None:
                print(current_parent_guide_recommendation_result.model_dump_json(indent=2))

            parent_message = await questionary.text("<Parent>: ",
                                                    default="오늘 학교에서 뭐 했니?" if current_parent_guide_recommendation_result is None and current_card_recommendation_result is None else "",
                                                    validate=make_non_empty_string_validator(
                                                        "A message should not be empty."), qmark="*").ask_async()
            current_card_recommendation_result = await session.submit_parent_message(parent_message, current_parent_guide_recommendation_result)
            current_interim_cards.clear()
            continue

        elif session.next_speaker == DialogueRole.Child and current_card_recommendation_result is not None:
            cards = current_card_recommendation_result.cards

            card_prompts = [card.simple_str() for card in cards]
            choices = ["[Refresh cards]"] + card_prompts

            submittable = current_interim_cards is not None and len(current_interim_cards) > 0
            if submittable:
                choices += ["[Submit]"]

            selection = await questionary.select(**{
                'choices': choices,
                'default': '[Refresh cards]',
                'message': f'Choose a word card. {"" if current_interim_cards is None or len(current_interim_cards) == 0 else ("Current selection: " + ", ".join([card.simple_str() for card in current_interim_cards]))}...'
            }).ask_async()

            if choices.index(selection) == 0:
                # refresh
                current_card_recommendation_result = await session.refresh_child_card_recommendation(
                    current_interim_cards, current_card_recommendation_result)
                continue
            elif submittable and choices.index(selection) == len(choices) - 1:
                # submit
                current_parent_guide_recommendation_result = await session.submit_child_selected_card(
                    current_interim_cards)

                current_card_recommendation_result = None
                current_interim_cards.clear()
                continue
            else:
                current_interim_cards.append(cards[choices.index(selection) - 1])
                current_card_recommendation_result = await session.refresh_child_card_recommendation(
                    current_interim_cards, None)
                continue
