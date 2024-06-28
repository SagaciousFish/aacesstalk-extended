from time import perf_counter
from typing import Any
from chatlib.utils.integration import APIAuthorizationVariableSpec, APIAuthorizationVariableSpecPresets, APIAuthorizationVariableType, IntegrationService
import httpx

# https://api.ncloud-docs.com/docs/ai-application-service-clovaspeech-shortsentence

class ClovaSpeech(IntegrationService):
    __url_spec = APIAuthorizationVariableSpec("invoke_url", "Invoke URL")
    __secret_spec = APIAuthorizationVariableSpecPresets.Secret

    @classmethod
    def provider_name(cls) -> str:
        return "Clova Speech"

    @classmethod
    def get_auth_variable_specs(cls) -> list[APIAuthorizationVariableSpec]:
        return [cls.__url_spec, cls.__secret_spec]

    @classmethod
    def _authorize_impl(cls, variables: dict[APIAuthorizationVariableSpec, Any]) -> bool:
        return True
    
    async def recognize_speech(self, file_name: str, file, content_type: str) -> str:
        self.assert_authorize()
        
        invoke_url = self.get_auth_variable_for_spec(self.__url_spec)
        secret = self.get_auth_variable_for_spec(self.__secret_spec)

        if invoke_url is not None and secret is not None:
            headers = {
                'Content-Type': 'application/octet-stream',
                'X-CLOVASPEECH-API-KEY': self.get_auth_variable_for_spec(self.__secret_spec)
            }

            t_s = perf_counter()

            async with httpx.AsyncClient() as client:
                response = await client.post(url=invoke_url + "?lang=Kor", files = {"file": (file_name, file, content_type)}, headers=headers)

            t_end = perf_counter()

            print(f"Clova speech recognition took {t_end - t_s} sec.")

            if response.status_code == 200:
                result = response.json()
                print(result)
                return result["text"]
            else:
                raise Exception("Clova speech error - ", response.status_code, response.json())
