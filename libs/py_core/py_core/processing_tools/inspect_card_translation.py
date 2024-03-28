import asyncio
import csv
import math

import questionary

from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams
from chatlib.llm.chat_completion_api import ChatCompletionAPI
from chatlib.tool.converter import generate_type_converter
from chatlib.llm.integration import GPTChatCompletionAPI, ChatGPTModel
from pydantic import BaseModel

from py_core.config import AACessTalkConfig

class TranslationRow(BaseModel):
    category: str
    word: str
    localized: str


class TranslationInspectionResult(BaseModel):
    passed: bool
    reason: str | None = None
    correction: str | None = None


def convert_translation_rows_to_str(rows: list[TranslationRow], params) -> str:
    return "\n".join([f"{row.category}, {row.word}, {row.localized}" for row in rows])


convert_str_to_inspections, convert_inspections_to_str = generate_type_converter(list[TranslationInspectionResult],
                                                                                 'yaml')


class CardTranslationFixer:
    def __init__(self, api: ChatCompletionAPI, filepath: str = AACessTalkConfig.card_translation_dictionary_path):
        self.__filepath = filepath

        self.__mapper = ChatCompletionFewShotMapper[
            list[TranslationRow], list[TranslationInspectionResult], ChatCompletionFewShotMapperParams](
            api,
            """
You are a helpful assistant that helps with inspecting English-Korean translation of keywords.
The keywords are intended to be written on word cards for Korean children to express their message to parents.

<INPUT>
The user will provide English-Korean translations in a comma-separated line listing Category, English, and Korean.

<OUTPUT>
Return the inspection result for the inputs in an YAML array, with each element containing the following variables:
- passed: boolean, whether the translation has passed the inspection or not.
- reason: Only if passed == false, describe why the translation was not passed.
- correction: Only if passed == false, Provide new Korean translation of the English keyword.

<INSPECTION POLICY>
- All translations, if describing actions or emotions, should take an honorific form, such as "~해요", "~어요".
- Words in the "Action" category should be verbs. Match the tense.
- Words in the "Topic" category should be nouns.

<EXAMPLES>

Input:
Action, do, 하다
emotion, sad, 슬픔
emotion, joyful, 기쁘다

Output:
-
  passed: false
  reason: Does not take an honorific form.
  correction: 해요
-
  passed: false
  reason: Emotions should be in a form of "~해요".
  correction: 슬퍼요
-
  passed: false
  reason: Emotions should be in a form of "~해요".
  correction: 기뻐요
            """, input_str_converter=convert_translation_rows_to_str,
            output_str_converter=convert_inspections_to_str,
            str_output_converter=convert_str_to_inspections
        )

    def __load_translation_list(self) -> list[TranslationRow]:
        with open(self.__filepath, mode='r', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)

            next(reader, None)

            rows: list[TranslationRow] = []
            for row in reader:
                rows.append(TranslationRow.model_validate(row))

            return rows

    async def inspect_all(self, check_mode = False):
        translations = self.__load_translation_list()

        inspections = await self.inspect(translations)

        failed_inspections = [(i, inspection) for i, inspection in enumerate(inspections) if inspection.passed is False]
        print(f"{len(failed_inspections)} translations failed to pass the inspection. Corrections suggested:")

        correction_applied = False
        for fi in failed_inspections:
            print(
                f"{translations[fi[0]].localized} ({translations[fi[0]].word}, {translations[fi[0]].category}) => {fi[1].correction} ({fi[1].reason})")
            if check_mode:
                confirmed = await questionary.confirm("Apply this suggestion?").ask_async()
                if confirmed:
                    translations[fi[0]].localized = fi[1].correction
                    correction_applied = True

        if correction_applied:
            with open(self.__filepath, mode='w', encoding='utf8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["category", "word", "localized"])
                writer.writerows([
                    [t.category, t.word, t.localized] for t in translations
                ])
            print("Reflected inspection result to file.")
    async def inspect(self, rows: list[TranslationRow], chunk_size=10) -> list[TranslationInspectionResult]:
        if len(rows) > chunk_size:
            print(f"Splitting {len(rows)} rows into {math.ceil(len(rows) / chunk_size)} chunks.")
            inspections = []
            for i in range(0, len(rows), chunk_size):
                inspections.extend(await self.inspect(rows[i:i + chunk_size]))

            return inspections
        else:
            print(f"Inspecting {len(rows)} translations..")
            inspections: list[TranslationInspectionResult] = await self.__mapper.run(None, rows,

                                                                                     ChatCompletionFewShotMapperParams(
                                                                                         model=ChatGPTModel.GPT_4_0613,
                                                                                         api_params={}))
            return inspections


if __name__ == "__main__":
    inspector = CardTranslationFixer(GPTChatCompletionAPI(), AACessTalkConfig.card_translation_dictionary_path)

    asyncio.run(inspector.inspect_all(check_mode=True))
