import asyncio
from os import path
from time import perf_counter

import questionary
from py_core.config import AACessTalkConfig
from py_core.system.model import UserLocale
from py_core.utils.speech import ClovaLongSpeech
from chatlib.global_config import GlobalConfig

from py_core.utils.speech.whisper import WhisperSpeechRecognizer

GlobalConfig.is_cli_mode = True

ENGINE_TYPE_CLOVA_SPEECH = "Clova Speech"
ENGINE_TYPE_OPENAI_WHISPER = "OpenAI Whisper"

engine_type = questionary.select("Select the engine type", choices=[ENGINE_TYPE_CLOVA_SPEECH, ENGINE_TYPE_OPENAI_WHISPER]).ask()

if engine_type == ENGINE_TYPE_CLOVA_SPEECH:
    ClovaLongSpeech.assert_authorize()
    engine = ClovaLongSpeech()

if engine_type == ENGINE_TYPE_OPENAI_WHISPER:
    WhisperSpeechRecognizer.assert_authorize()
    engine = WhisperSpeechRecognizer()


t_s = perf_counter()

file = open(path.join(AACessTalkConfig.dataset_dir_path, "samples/clova_sample_voice_2.m4a"), 'rb')

#text = asyncio.run(engine.recognize_speech("clova_sample_voice.m4a", file, "audio/m4a"))

resp = asyncio.run(engine.recognize_speech("clova_sample_voice.m4a", file, "audio/m4a", UserLocale.Korean, "다솜이"))

t_e = perf_counter()

print(f"Conversion took {t_e - t_s} sec.")

print(resp)