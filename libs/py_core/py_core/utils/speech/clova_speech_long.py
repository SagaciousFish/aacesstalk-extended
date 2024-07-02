import tempfile
from time import perf_counter
import os
from typing import Any
from chatlib.utils.integration import APIAuthorizationVariableSpec, APIAuthorizationVariableSpecPresets, APIAuthorizationVariableType, IntegrationService
import httpx
from pydub import AudioSegment
from retry import retry
import json

# https://api.ncloud-docs.com/docs/ai-application-service-clovaspeech-shortsentence

class ClovaLongSpeech(IntegrationService):
    __url_spec = APIAuthorizationVariableSpec("invoke_url", "Invoke URL")
    __secret_spec = APIAuthorizationVariableSpecPresets.Secret

    @classmethod
    def provider_name(cls) -> str:
        return "Clova Speech Long Sentence API"

    @classmethod
    def get_auth_variable_specs(cls) -> list[APIAuthorizationVariableSpec]:
        return [cls.__url_spec, cls.__secret_spec]

    @classmethod
    def _authorize_impl(cls, variables: dict[APIAuthorizationVariableSpec, Any]) -> bool:
        return True
    
    @retry(tries=5, delay=0.5)
    async def recognize_speech(self, file_name: str, file, content_type: str) -> str:
        self.assert_authorize()
        
        invoke_url = self.get_auth_variable_for_spec(self.__url_spec)
        secret = self.get_auth_variable_for_spec(self.__secret_spec)

        if invoke_url is not None and secret is not None:

            url = invoke_url + "/recognizer/upload"

            headers = {
                'X-CLOVASPEECH-API-KEY': secret
            }

            form_data = {
                "params": json.dumps({
                    "language": "ko-KR",
                    "completion": "sync",
                })
            }
            # Construct multipart/form-data
            multipart_data = []

            # Add form fields to multipart data
            for key, value in form_data.items():
                multipart_data.append((key, (None, value)))

            # Add files to multipart data
            multipart_data.append(("media", (file_name, file, content_type)))


            t_s = perf_counter()

            async with httpx.AsyncClient() as client:
                    response = await client.post(url=url, files = multipart_data, headers=headers)

            t_end = perf_counter()

            print(f"Clova speech recognition took {t_end - t_s} sec.")

            if response.status_code == 200:
                result = response.json()
                
                print(result)
                return result["text"]
            else:
                print(response.json())
                raise Exception("Clova speech error - ", response.status_code)
