import asyncio

from py_core.utils.speech.clova_voice import ClovaVoice, ClovaVoiceParams
from chatlib.global_config import GlobalConfig

GlobalConfig.is_cli_mode = True
ClovaVoice.assert_authorize()

cv = ClovaVoice()

file_path = asyncio.run(cv.create_voice("액세스톡은 자폐 스펙트럼 장애를 가진 아동과 부모 간의 의사소통을 돕는 AI기반 맥락형 기술입니다.", ClovaVoiceParams(pitch=3)))

print(file_path)