import csv
from contextlib import AbstractContextManager

from time import perf_counter
from typing import TypeAlias
from os import path

from py_core.utils.translation_types import DictionaryRow
from py_core.utils.vector_db import VectorDB

LookupDictionary: TypeAlias = dict[tuple[str, str], DictionaryRow]


class LookupTranslator(AbstractContextManager):

    def __init__(self, dict_filepath: str | None = None, verbose: bool = False):
        self.__dictionary: LookupDictionary = dict()
        self.verbose = verbose
        self.__dict_filepath: str | None = dict_filepath

        self.__vector_db = VectorDB()

        self.load_file()

    @property
    def vector_db(self) -> VectorDB:
        return self.__vector_db

    def load_file(self):
        if self.__dict_filepath is not None:
            if path.exists(self.__dict_filepath):
                if self.verbose:
                    print(f"Loading a dictionary file...")
                t_start = perf_counter()
                with open(self.__dict_filepath, mode='r', encoding='utf8') as csvfile:
                    reader = csv.DictReader(csvfile, fieldnames=DictionaryRow.field_names())
                    next(reader, None)

                    num_lines = 0
                    for row in reader:
                        row_model = DictionaryRow.model_validate(row)

                        if row_model.lookup_key not in self.dictionary:
                            self.__dictionary[row_model.lookup_key] = row_model
                        num_lines += 1

                    self.__vector_db.upsert_cards([row for k, row in self.__dictionary.items()])

                t_end = perf_counter()

                if self.verbose:
                    print(f"File dictionary loading ({num_lines} entries) took {t_end - t_start} sec.")
            else:
                if self.verbose:
                    print(f"Dictionary file does not exist. Skip reading.")
        else:
            if self.verbose:
                print(f"Dictionary file path was not set.")

    def write_to_file(self):
        if self.__dict_filepath is not None:
            if self.verbose:
                print("Write lookup dictionary to file..")

            with open(self.__dict_filepath, mode='w', encoding='utf8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=DictionaryRow.field_names())
                writer.writeheader()

                items = [v for k, v in self.__dictionary.items()]

                items.sort(key=lambda elm: elm.localized)
                items.sort(key=lambda elm: elm.word)
                items.sort(key=lambda elm: elm.category)

                for row_model in items:
                    writer.writerow(row_model.model_dump())

    @property
    def dictionary(self) -> LookupDictionary:
        return self.__dictionary

    @property
    def size(self) -> int:
        return len(self.__dictionary)

    def lookup(self, word: str, category: str) -> str | None:
        key = (word, category)
        if key in self.dictionary:
            return self.dictionary[key].localized

    def update(self, word: str, category: str, localized: str):
        row = DictionaryRow(category=category, word=word, localized=localized)
        self.dictionary[(word, category)] = row
        self.__vector_db.upsert_cards(row)

    def query_similar_cards(self, word: str | list[str], category: str, k: int = 5) -> list[DictionaryRow]:
        return self.__vector_db.query_similar_cards(word, category, k)

    def __aenter__(self):
        return self

    def __exit__(self, __exc_type, __exc_value, __traceback):
        self.write_to_file()
