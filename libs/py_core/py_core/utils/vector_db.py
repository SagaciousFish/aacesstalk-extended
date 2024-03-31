from os import path

import chromadb
import chromadb.utils.embedding_functions as ef

from chatlib.llm.integration import GPTChatCompletionAPI
from chatlib.utils.integration import APIAuthorizationVariableSpec, APIAuthorizationVariableType
from chromadb.api.models.Collection import Collection
from numpy import ndarray

from py_core.config import AACessTalkConfig
from py_core.utils.translation_types import DictionaryRow


class VectorDB:

    def __init__(self, dir_name: str = "embeddings", embedding_model: str = "text-embedding-3-small"):
        #self.__client = chromadb.PersistentClient(path.join(AACessTalkConfig.dataset_dir_path, dir_name))
        self.__client = chromadb.Client()

        GPTChatCompletionAPI.assert_authorize()
        api_key = GPTChatCompletionAPI.get_auth_variable_for_spec(
            APIAuthorizationVariableSpec(APIAuthorizationVariableType.ApiKey))

        self.__decode = ef.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=embedding_model
        )

        self.__collection_cards = self.__client.get_or_create_collection("cards", embedding_function=self.__decode)

    @property
    def collection_cards(self) -> Collection:
        return self.__collection_cards

    def upsert_cards(self, dictionary_row: DictionaryRow | list[DictionaryRow]) -> ndarray | list[ndarray]:
        rows = [dictionary_row] if isinstance(dictionary_row, DictionaryRow) else dictionary_row

        self.collection_cards.upsert(
            ids=[row.id for row in rows],
            metadatas=[row.model_dump(include={"category", "localized"}) for row in rows],
            documents=[row.word for row in rows]
        )

    def query_similar_cards(self, word: str | list[str], category: str, k: int = 5) -> list[DictionaryRow]:
        print(f"Query similar cards: {word}, {category}")
        query_result = self.collection_cards.query(query_texts=[word] if isinstance(word, str) else word,
                                                     n_results=k, where={"category": category})
        if len(query_result["ids"][0]) > 0:
            return [DictionaryRow(id=id, word=doc, category=meta["category"], localized=meta["localized"]) for
                    id, doc, meta in zip(query_result["ids"][0], query_result["documents"][0], query_result["metadatas"][0])]
        else:
            return []
