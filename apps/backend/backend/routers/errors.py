from enum import StrEnum


class ErrorType(StrEnum):
    NoSuchUser = "NoSuchUser"
    EmptyDictation = "EmptyDictation"
    DictationFail = "DictationFail"