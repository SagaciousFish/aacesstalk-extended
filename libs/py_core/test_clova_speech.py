import asyncio
from os import path
from time import perf_counter
from py_core.config import AACessTalkConfig
from py_core.utils.speech import ClovaSpeech, ClovaLongSpeech
from chatlib.global_config import GlobalConfig

GlobalConfig.is_cli_mode = True
ClovaSpeech.assert_authorize()
ClovaLongSpeech.assert_authorize()

engine = ClovaSpeech()
enging_long = ClovaLongSpeech()

t_s = perf_counter()

file = open(path.join(AACessTalkConfig.dataset_dir_path, "samples/clova_sample_voice_2.m4a"), 'rb')

#text = asyncio.run(engine.recognize_speech("clova_sample_voice.m4a", file, "audio/m4a"))

resp = asyncio.run(enging_long.recognize_speech("clova_sample_voice.m4a", file, "audio/m4a"))

t_e = perf_counter()

print(f"Conversion took {t_e - t_s} sec.")

print(text)