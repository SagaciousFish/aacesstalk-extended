from abc import ABC, abstractmethod

from retry import retry

from py_core.system.model import UserLocale

class SpeechRecognizerBase(ABC):
    
    @abstractmethod
    @retry(tries=5, delay=0.5)
    async def recognize_speech(self, file_name: str, file, content_type: str, locale: UserLocale, child_name: str) -> str:
        pass