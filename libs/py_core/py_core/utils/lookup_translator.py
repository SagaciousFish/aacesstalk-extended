import csv
from contextlib import AbstractContextManager

from time import perf_counter
from typing import TypeAlias
import aiofiles
from os import path

LookupDictionary: TypeAlias = dict[tuple[str, str], str]


class LookupTranslator(AbstractContextManager):

    def __init__(self, dict_filepath: str | None = None, verbose: bool = False):
        self.__dictionary: LookupDictionary = dict()
        self.verbose = verbose
        self.__dict_filepath: str | None = dict_filepath

    def load_file(self):
        if self.__dict_filepath is not None:
            if path.exists(self.__dict_filepath):
                if self.verbose:
                    print(f"Loading a dictionary file...")
                t_start = perf_counter()
                with open(self.__dict_filepath, mode='r', encoding='utf8') as csvfile:
                    reader = csv.reader(csvfile)

                    next(reader, None)

                    num_lines = 0
                    for row in reader:
                        print(row)
                        if (row[1], row[0]) not in self.dictionary:
                            self.__dictionary[(row[1], row[0])] = row[2]
                        num_lines += 1

                t_end = perf_counter()

                if self.verbose:
                    print(f"File dictionary loading ({num_lines} entries) took {t_end - t_start} sec.")
            else:
                if self.verbose:
                    print(f"Dictionary file does not exist. Skip reading.")
        else:
            if self.verbose:
                print(f"Dictionary file path was not set.")

    async def load_file_async(self):
        if self.__dict_filepath is not None:
            if path.exists(self.__dict_filepath):
                if self.verbose:
                    print(f"Loading a dictionary file...")
                t_start = perf_counter()
                async with aiofiles.open(self.__dict_filepath, mode='r', encoding='utf8') as csvfile:
                    reader = csv.reader(await csvfile.read())

                    next(reader, None)

                    num_lines = 0
                    for row in reader:
                        if (row[1], row[0]) not in self.dictionary:
                            self.__dictionary[(row[1], row[0])] = row[2]
                        num_lines += 1

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
                writer = csv.writer(csvfile)

                writer.writerow(["category", "word", "localized"])

                for (word, category), localized in self.__dictionary.items():
                    writer.writerow([category, word, localized])

    @property
    def dictionary(self) -> LookupDictionary:
        return self.__dictionary

    @property
    def size(self) -> int:
        return len(self.__dictionary)

    def lookup(self, word: str, category: str) -> str | None:
        key = (word, category)
        if key in self.dictionary:
            return self.dictionary[key]

    def update(self, word: str, category: str, localized: str):
        self.dictionary[(word, category)] = localized

    def __aenter__(self):
        return self

    def __exit__(self, __exc_type, __exc_value, __traceback):
        self.write_to_file()
