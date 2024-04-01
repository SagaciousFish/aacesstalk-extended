from functools import cached_property

from nanoid import generate
from pydantic import BaseModel, ConfigDict, Field


class DictionaryRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=lambda: generate(size=10))
    category: str
    english: str
    localized: str
    inspected: bool = False

    @classmethod
    def field_names(cls) -> list[str]:
        return [k for k, v in cls.model_fields.items()]

    @cached_property
    def lookup_key(self) -> tuple[str, str]:
        return self.english, self.category
