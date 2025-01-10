from typing import Any
from chatlib.utils.integration import APIAuthorizationVariableSpec, IntegrationService
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI
from chatlib.utils.env_helper import get_env_variable
from openai import AsyncOpenAI
from py_core.utils.speech.speech_recognizer_base import SpeechRecognizerBase

from py_core.system.model import UserLocale


class WhisperSpeechRecognizer(SpeechRecognizerBase, IntegrationService):
    @classmethod
    def provider_name(cls) -> str:
        return "Whisper Speech API"

    @classmethod
    def get_auth_variable_specs(cls) -> list[APIAuthorizationVariableSpec]:
        return GPTChatCompletionAPI.get_auth_variable_specs()

    @classmethod
    def _authorize_impl(cls, variables: dict[APIAuthorizationVariableSpec, Any]) -> bool:
        return GPTChatCompletionAPI._authorize_impl(variables)
    
    @classmethod
    def assert_authorize(cls):
        return GPTChatCompletionAPI.assert_authorize()
    
    async def recognize_speech(self, file_name: str, file, content_type: str, locale: UserLocale, child_name: str) -> str:
        self.assert_authorize()        

        client: AsyncOpenAI = AsyncOpenAI(api_key=get_env_variable("OPEN_A_I_API_KEY"))

        try:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=file,
                response_format="json",
                language="en" if locale == UserLocale.English else "ko",
                prompt=f"This is a conversation between a parent and a child. The parent is talking to the child named {child_name}.",
            )

            return transcription.text
        except Exception as e:
            raise Exception(f"Failed to recognize speech: {e}")
            