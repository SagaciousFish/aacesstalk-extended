import questionary
from chatlib.utils.validator import make_non_empty_string_validator

from py_core import ModeratorSession
from py_core.system.model import ChildCardRecommendationResult, ParentGuideRecommendationResult, CardInfo, DialogueRole, \
    ParentGuideType, ParentExampleMessage, InterimCardSelection


async def test_session_loop(session: ModeratorSession):
    while True:
        if session.next_speaker == DialogueRole.Parent:
            current_parent_guide_recommendation_result = await session.storage.get_latest_parent_guide_recommendation()
            if current_parent_guide_recommendation_result is not None:
                print(current_parent_guide_recommendation_result.model_dump_json(indent=2))
                if len(current_parent_guide_recommendation_result.messaging_guides) > 0:
                    while True:
                        enter_parent_message = "Enter parent message"
                        choices = []
                        choices.extend([f"Show example message for \"{guide.guide_localized}\"" for guide in
                                        current_parent_guide_recommendation_result.messaging_guides])
                        choices.append(enter_parent_message)
                        selection = await questionary.select(
                            message="Choose an option.",
                            choices=choices,
                            default="Enter parent message"
                        ).ask_async()

                        if choices.index(selection) < len(choices) - 1:
                            guide = current_parent_guide_recommendation_result.messaging_guides[
                                choices.index(selection)]
                            example_message: ParentExampleMessage = await session.request_parent_example_message(
                                current_parent_guide_recommendation_result.id, guide_id=guide.id)
                            questionary.print(f"\"{example_message.message_localized}\" ({example_message.message})",
                                              style="bold italic fg:green")
                        else:
                            break

            parent_message = await questionary.text("<Parent>: ",
                                                    default="오늘 학교에서 뭐 했니?" if len(
                                                        await session.storage.get_dialogue()) == 0 else "",
                                                    validate=make_non_empty_string_validator(
                                                        "A message should not be empty."), qmark="*").ask_async()
            await session.submit_parent_message(parent_message)
            continue

        elif session.next_speaker == DialogueRole.Child:
            current_card_recommendation_result = await session.storage.get_latest_child_card_recommendation()
            if current_card_recommendation_result is not None:
                cards = current_card_recommendation_result.cards

                card_prompts = [card.simple_str() for card in cards]
                choices = ["[Refresh cards]"] + card_prompts

                current_interim_card_selection = await session.storage.get_latest_card_selection()
                current_interim_cards = await session.get_card_info_from_identities(
                    current_interim_card_selection.cards) if current_interim_card_selection is not None else []
                submittable = len(current_interim_cards) > 0
                if submittable:
                    choices += ["[Submit]"]

                selection = await questionary.select(
                    choices=choices,
                    default='[Refresh cards]',
                    message=f'Choose a word card. {"" if current_interim_cards is None or len(current_interim_cards) == 0 else ("Current selection: " + ", ".join([card.simple_str() for card in current_interim_cards]))}...'
                ).ask_async()

                if choices.index(selection) == 0:
                    # refresh
                    await session.refresh_child_card_recommendation()
                    continue
                elif submittable and choices.index(selection) == len(choices) - 1:
                    # submit
                    await session.confirm_child_card_selection()
                    continue
                else:
                    # select
                    await session.select_child_card(cards[choices.index(selection) - 1])
                    await session.refresh_child_card_recommendation()
                    continue
