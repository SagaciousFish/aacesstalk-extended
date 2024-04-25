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
from py_core.utils.models import DictionaryRow


class TranslationInspectionResult(BaseModel):
    passed: bool
    reason: str | None = None
    correction: str | None = None


def convert_translation_rows_to_str(rows: list[DictionaryRow], params) -> str:
    return "\n".join([f"{row.category}, {row.english}, {row.localized}" for row in rows])


convert_str_to_inspections, convert_inspections_to_str = generate_type_converter(list[TranslationInspectionResult],
                                                                                 'yaml')


class CardTranslationFixer:
    def __init__(self, api: ChatCompletionAPI, filepath: str = AACessTalkConfig.card_translation_dictionary_path):
        self.__filepath = filepath

        self.__mapper = ChatCompletionFewShotMapper[
            list[DictionaryRow], list[TranslationInspectionResult], ChatCompletionFewShotMapperParams](
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

    def __load_translation_list(self) -> list[DictionaryRow]:
        with open(self.__filepath, mode='r', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)

            next(reader, None)

            rows: list[DictionaryRow] = []
            for row in reader:
                rows.append(DictionaryRow.model_validate(row))

            return rows

    async def inspect_all(self, check_mode = False):
        translations = self.__load_translation_list()

        translations_already_inspected = [trans for trans in translations if trans.inspected is True]
        translations_to_inspect = [trans for trans in translations if trans.inspected is False]

        if len(translations_to_inspect) > 0:
            inspections = await self.inspect(translations_to_inspect)

            successful_inspections = [(i, inspection) for i, inspection in enumerate(inspections) if inspection.passed is True]
            for i, ins in successful_inspections:
                d = translations_to_inspect[i].model_dump()
                d["inspected"] = True
                translations_to_inspect[i] = DictionaryRow(**d)

            failed_inspections = [(i, inspection) for i, inspection in enumerate(inspections) if inspection.passed is False]
            print(f"{len(failed_inspections)} translations failed to pass the inspection. Corrections suggested:")

            correction_applied = False
            for fi in failed_inspections:
                print(
                    f"{translations_to_inspect[fi[0]].localized} ({translations_to_inspect[fi[0]].english}, {translations_to_inspect[fi[0]].category}) => {fi[1].correction} ({fi[1].reason})")
                if check_mode:
                    confirmed = await questionary.confirm("Apply this suggestion?").ask_async()
                    if confirmed:
                        d = translations_to_inspect[fi[0]].model_dump()
                        d["localized"] = fi[1].correction
                        d["inspected"] = True
                        translations_to_inspect[fi[0]] = DictionaryRow(**d)
                        correction_applied = True
                    else:
                        d = translations_to_inspect[fi[0]].model_dump()
                        d["inspected"] = True
                        translations_to_inspect[fi[0]] = DictionaryRow(**d)

            with open(self.__filepath, mode='w', encoding='utf8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=DictionaryRow.field_names())
                writer.writeheader()
                translations = translations_already_inspected + translations_to_inspect

                translations.sort(key=lambda t: t.label_localized)
                translations.sort(key=lambda t: t.english)
                translations.sort(key=lambda t: t.category)

                for t in translations:
                    writer.writerow(t.model_dump())

            print("Reflected inspection result to file.")
        else:
            print("No translations to be inspected.")

    async def inspect(self, rows: list[DictionaryRow], chunk_size=10) -> list[TranslationInspectionResult]:
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
