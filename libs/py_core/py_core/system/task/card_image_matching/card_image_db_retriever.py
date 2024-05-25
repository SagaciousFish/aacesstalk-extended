from csv import DictReader
from time import perf_counter

import numpy

from py_core.config import AACessTalkConfig
from py_core.utils.models import CardImageInfo
from py_core.utils.vector_db import VectorDB


class CardImageDBRetriever:
    def __init__(self):
        print("Initialize card image DB retriever.")
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

    def __query_result_to_info_list(self, query_result) -> list[list[tuple[CardImageInfo, float]]]:
        list_length = len(query_result["ids"])

        result = []
        for i in range(list_length):
            print(i)        
            if len(query_result["ids"][i]) > 0:
                objs = [self.__card_info_dict[id] for id in query_result["ids"][i]]
                distances = [s for s in query_result["distances"][i]]
                result.append([(o,d) for o,d in zip(objs, distances)])
            else:
                result.append([])
        
        return result

    def __query_nearest_card_image_info_single(self, name: str, k=3)->list[list[CardImageInfo]]:
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
            name_query_result = self.__query_result_to_info_list(name_query_result)[0]
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

    def query_nearest_card_image_infos(self, names: list[str], k=3)->list[list[CardImageInfo]]:
        t_start = perf_counter()
        #First, find exact match.
        name_result_dict: dict[str, list[CardImageInfo]|None] = {name:None for name in names}
        
        name_match_results = self.__collection_name.get(where={"name": {"$in": names}})

        for id in name_match_results["ids"]:
            card_image_info = self.__card_info_dict[id]
            name_result_dict[card_image_info.name_en] = [card_image_info]

        no_name_matched_card_names = [name for name in names if (name not in name_result_dict or name_result_dict[name] is None or len(name_result_dict[name]) == 0)]
        
        if len(no_name_matched_card_names) > 0:
            # Find fuzzy name match.
            print("Find fuzzy name match.")
            name_query_results = self.__collection_name.query(
                query_texts=no_name_matched_card_names,
                n_results=k
            )
            name_query_results = self.__query_result_to_info_list(name_query_results)
            print(name_query_results)

            for i, name in enumerate(no_name_matched_card_names):
                name_result_dict[name] = [tup[0] for tup in name_query_results[i]]

                      

            #result = self.__collection_desc.query(
            #    query_texts=[name],
            #    n_results=k
            #)
            #return [tup[0] for tup in self.__query_result_to_info_list(result)]
        
        result = [name_result_dict[name] for name in names]  

        t_end = perf_counter()
        print(f"Card retrieval took {t_end - t_start} sec.")

        return result