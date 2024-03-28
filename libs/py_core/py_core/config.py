from os import path, getcwd


class AACessTalkConfig:
    dataset_dir_path: str = path.join(getcwd(), "../../data")
    card_translation_dictionary_path: str = path.join(dataset_dir_path, "card_translation_dictionary.csv")
