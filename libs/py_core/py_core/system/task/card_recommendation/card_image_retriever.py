from csv import DictReader

import numpy

from py_core.config import AACessTalkConfig
from py_core.utils.models import CardImageInfo
from py_core.utils.vector_db import VectorDB


class CardImageRetriever:
    def __init__(self):
        info_list: list[CardImageInfo] = []
        with open(AACessTalkConfig.card_image_table_path, 'r') as f:
            reader = DictReader(f, fieldnames=CardImageInfo.model_fields)
            next(reader)
            for row in reader:
                info_list.append(CardImageInfo(**row))

        self.__card_info_dict = {inf.id:inf for inf in info_list}

        embedding_store = numpy.load(AACessTalkConfig.card_image_embeddings_path)
        ids = embedding_store["ids"]
        embeddings = embedding_store["embeddings"]

        self.__vector_db = VectorDB(embedding_model=AACessTalkConfig.embedding_model,
                                    embedding_dimensions=AACessTalkConfig.embedding_dimensions)

        self.__collection = self.__vector_db.get_collection("card_image_desc")
        self.__collection.add(
            ids=[id for id in ids],
            documents=[info.description_brief for info in info_list],
            metadatas=[info.model_dump(include={"name", "category"}) for info in info_list],
            embeddings=[emb.tolist() for emb in embeddings]
        )

    def query_nearest_card_image_infos(self, keyword: str, k=3)->list[CardImageInfo]:
        result = self.__collection.query(
            query_texts=[keyword],
            n_results=k
        )

        if len(result["ids"][0]) > 0:
            return [self.__card_info_dict[id] for id in result["ids"][0]]


