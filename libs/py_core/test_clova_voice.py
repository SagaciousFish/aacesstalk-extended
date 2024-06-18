import asyncio

from py_core.utils.tts.clova_voice import ClovaVoice, ClovaVoiceParams
from chatlib.global_config import GlobalConfig

GlobalConfig.is_cli_mode = True
ClovaVoice.assert_authorize()

cv = ClovaVoice()

file_path = asyncio.run(cv.create_voice("즐거워요.", ClovaVoiceParams(pitch=3)))

print(file_path)