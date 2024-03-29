from py_core.system.model import Dialogue, DialogueRole


def convert_dialogue_to_str(dialogue: Dialogue, params) -> str:
    script = "\n".join([
        f"\t<msg>{'Parent' if message.role == DialogueRole.Parent else 'Child'}: {message.content_en if isinstance(message.content, str) else ', '.join([card.text for card in message.content])}</msg>"
        for message in dialogue])

    result = f"""
<dialogue>
{script}
</dialogue>"""
    return result
