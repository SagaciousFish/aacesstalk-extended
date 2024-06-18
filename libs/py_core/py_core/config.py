from os import path, getcwd


class AACessTalkConfig:
    dataset_dir_path: str = path.join(getcwd(), "../../data")

    card_translation_dictionary_path: str = path.join(dataset_dir_path, "card_translation_dictionary.csv")
    parent_example_translation_dictionary_path: str = path.join(dataset_dir_path, "parent_example_translation_dictionary.csv")
    card_image_directory_path: str = path.join(dataset_dir_path, "cards")
    card_image_table_path: str = path.join(dataset_dir_path, "cards_image_info.csv")
    default_core_card_table_path: str = path.join(dataset_dir_path, "default_core_cards.yml")
    default_emotion_card_table_path: str = path.join(dataset_dir_path, "default_emotion_cards.yml")
    initial_parent_guides_path: str = path.join(dataset_dir_path, "initial_parent_guides.yml")
    card_image_embeddings_path: str = path.join(dataset_dir_path, "cards_image_desc_embeddings.npz")

    database_dir_path: str = path.join(getcwd(), "../../database")

    cache_dir_path: str = path.join(database_dir_path, "cache")

    voiceover_cache_dir_path: str = path.join(cache_dir_path, "voiceover")


    embedding_model = 'text-embedding-3-large'
    embedding_dimensions = 256
