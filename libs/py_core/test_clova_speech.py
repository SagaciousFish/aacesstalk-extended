import asyncio
from os import path
from time import perf_counter
from py_core.config import AACessTalkConfig
from py_core.utils.speech import ClovaSpeech
from chatlib.global_config import GlobalConfig
from pydub import AudioSegment

GlobalConfig.is_cli_mode = True
ClovaSpeech.assert_authorize()

engine = ClovaSpeech()

t_s = perf_counter()

file = open(path.join(AACessTalkConfig.dataset_dir_path, "samples/clova_sample_voice.m4a"), 'rb')

converted_file_path = path.join(AACessTalkConfig.dataset_dir_path, "samples/clova_sample_voice_converted.mp3")

audio = AudioSegment.from_file(file, format='m4a')
audio.export(converted_file_path, format='mp3')

text = asyncio.run(engine.recognize_speech("clova_sample_voice_converted.mp3", open(path.join(AACessTalkConfig.dataset_dir_path, "samples/clova_sample_voice.mp3"), 'rb'), "audio/mpeg"))

t_e = perf_counter()

print(f"Conversion took {t_e - t_s} sec.")

print(text)