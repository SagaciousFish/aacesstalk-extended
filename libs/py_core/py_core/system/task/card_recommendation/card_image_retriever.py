from csv import DictReader
from time import perf_counter

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
        desc_embeddings = embedding_store["emb_desc"]
        name_embeddings = embedding_store["emb_name"]

        self.__vector_db = VectorDB(embedding_model=AACessTalkConfig.embedding_model,
                                    embedding_dimensions=AACessTalkConfig.embedding_dimensions)

        self.__collection_desc = self.__vector_db.get_collection("card_image_desc")
        self.__collection_desc.add(
            ids=[id for id in ids],
            documents=[info.description_brief for info in info_list],
            metadatas=[info.model_dump(include={"name", "category"}) for info in info_list],
            embeddings=[emb.tolist() for emb in desc_embeddings]
        )

        self.__collection_name = self.__vector_db.get_collection("names")
        self.__collection_name.add(
            ids=[id for id in ids],
            documents=[info.name for info in info_list],
            metadatas=[info.model_dump(include={"name", "category", "description_brief"}) for info in info_list],
            embeddings=[emb.tolist() for emb in name_embeddings]
        )

    def __query_result_to_info_list(self, query_result) -> list[tuple[CardImageInfo, float]]:
        if len(query_result["ids"][0]) > 0:
            objs = [self.__card_info_dict[id] for id in query_result["ids"][0]]
            distances = [s for s in query_result["distances"][0]]
            return [(o,d) for o,d in zip(objs, distances)]
        else:
            return []

    def query_nearest_card_image_infos(self, name: str, k=3)->list[CardImageInfo]:
        t_start = perf_counter()
        #First, find exact match.
        name_match_result = self.__collection_name.get(where={"name": name})
        if len(name_match_result["ids"]) > 0:
            print("Found exact name match.")
            result = [self.__card_info_dict[id] for id in name_match_result["ids"]]
        else:
            # Find fuzzy name match.
            print("Find fuzzy name match.")
            name_query_result = self.__collection_name.query(
                query_texts=[name],
                n_results=k
            )
            name_query_result = self.__query_result_to_info_list(name_query_result)
            print(name_query_result)

            result = [tup[0] for tup in name_query_result]

            #result = self.__collection_desc.query(
            #    query_texts=[name],
            #    n_results=k
            #)
            #return [tup[0] for tup in self.__query_result_to_info_list(result)]

        t_end = perf_counter()
        print(f"Card retrieval took {t_end - t_start} sec.")

        return result
