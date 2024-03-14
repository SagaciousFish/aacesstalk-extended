from py_core.system.model import Dialogue, DialogueRole


def convert_dialogue_to_str(dialogue: Dialogue, params) -> str:
    script = "\n".join([
        f"\t<msg>{'Parent' if message.speaker == DialogueRole.Parent else 'Child'}: {message.content if isinstance(message.content, str) else ', '.join([card.simple_str() for card in message.content])}</msg>"
        for message in dialogue])

    result = f"""
<dialogue>
{script}
</dialogue>"""
    print(result)
    return result
