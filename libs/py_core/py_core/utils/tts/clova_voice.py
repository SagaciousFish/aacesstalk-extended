from functools import cached_property
from os import path
from time import perf_counter
from typing import Any, Literal, Union
from chatlib.utils.integration import APIAuthorizationVariableSpec, APIAuthorizationVariableSpecPresets, APIAuthorizationVariableType, IntegrationService
import pendulum
from pydantic import BaseModel, ConfigDict, Field
import requests
import hashlib
from diskcache import Cache
from asyncio import to_thread
from nanoid import generate

from py_core.config import AACessTalkConfig

# https://api.ncloud-docs.com/docs/ai-naver-clovavoice


class ClovaVoiceParams(BaseModel):
    speaker: str = "vdain"
    speed: int = 0
    volume: int = 0
    pitch: int = 0
    emotion: int = 0
    emotion_strength: int = Field(alias="emotion-strength", default=1)
    format: Union[Literal["mp3"], Literal["wav"]] = 'mp3'

class CacheKeyParams(ClovaVoiceParams):

    model_config = ConfigDict(frozen=True)

    text: str
    service: str = "clova"


    @cached_property
    def cache_key(self)->str:
        params_string = self.model_dump_json()
        return hashlib.md5(params_string.encode()).hexdigest()


class ClovaVoice(IntegrationService):

    ENDPOINT_TTS = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

    __client_id_spec = APIAuthorizationVariableSpecPresets.ApiKey
    __client_secret_spec = APIAuthorizationVariableSpecPresets.Secret


    def __init__(self):
        super().__init__()


    @classmethod
    def provider_name(cls) -> str:
        return "Clova Voice"

    @classmethod
    def get_auth_variable_specs(cls) -> list[APIAuthorizationVariableSpec]:
        return [cls.__client_id_spec, cls.__client_secret_spec]

    @classmethod
    def _authorize_impl(cls, variables: dict[APIAuthorizationVariableSpec, Any]) -> bool:
        return True

    

    async def create_voice(self, text: str, params: ClovaVoiceParams) -> str:

        with Cache(AACessTalkConfig.voiceover_cache_dir_path) as cache:
            cache_params = CacheKeyParams(**params.model_dump(), text=text, service="clova")
            if cache_params.cache_key in cache:
                print(f"Use cached voiceover file for \"{text}\"...")
                if path.exists(cache[cache_params.cache_key]):
                    return cache[cache_params.cache_key]
                else:
                    cache.delete(cache_params.cache_key)
                    print("Cached file does not exist. Invalidate cache and regenerate the audio...")
                

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-NCP-APIGW-API-KEY-ID" : self.get_auth_variable_for_spec(self.__client_id_spec),
                "X-NCP-APIGW-API-KEY" : self.get_auth_variable_for_spec(self.__client_secret_spec)
            }

            body = params.model_dump(by_alias=True)
            body["text"] = text

            t_s = perf_counter()

            response = await to_thread(requests.post, url=self.ENDPOINT_TTS, data=body, headers=headers)

            t_end = perf_counter()

            print(f"Clova Voice generation took {t_end - t_s} sec.")

            if response.status_code == 200:
                
                file_path = None
                while True:
                    timestamp = pendulum.now().format("YYYY-MM-DD-HH-mm-ss", locale="en")
                    file_path = path.join(AACessTalkConfig.voiceover_cache_dir_path, f"voiceover_{timestamp}_{generate(size=8)}.mp3")

                    if not path.exists(file_path):
                        break
                


                with open(file_path, 'wb') as fp:
                    fp.write(response.content)
                    
                cache.set(cache_params.cache_key, file_path)
                return file_path
            else:
                print(response.status_code, response.json())
                raise Exception("Voiceover generation failed.")