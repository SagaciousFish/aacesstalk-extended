import asyncio
from csv import DictReader
from time import perf_counter

import re
import numpy
from pandas import DataFrame

from py_core.config import AACessTalkConfig
from py_core.utils.models import CardImageInfo
from py_core.utils.vector_db import VectorDB
from py_core.system.model import CardInfo


def normalize_korean(text: str) -> str:
    return re.sub(r'[^\w]|\_', '', text.strip().lower())

class CardImageDBRetriever:
    def __init__(self):
        print("Initialize card image DB retriever.")
        info_list: list[CardImageInfo] = []
        with open(AACessTalkConfig.card_image_table_path, 'r', encoding='utf-8') as f:
            reader = DictReader(f, fieldnames=CardImageInfo.model_fields)
            next(reader)
            for row in reader:
                info_list.append(CardImageInfo(**row))

        self.__card_info_dict = {inf.id:inf for inf in info_list}        

        self.__card_info_table = DataFrame(data=[inf.model_dump() for inf in info_list])
        self.__card_info_table['name_ko_nm'] = self.__card_info_table.name_ko.apply(normalize_korean)     

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
            metadatas=[info.model_dump(include={"name", "name_ko", "category", "filename"}) for info in info_list],
            embeddings=[emb.tolist() for emb in desc_embeddings]
        )

        self.__collection_name = self.__vector_db.get_collection("names")
        self.__collection_name.add(
            ids=[id for id in ids],
            documents=[info.name for info in info_list],
            metadatas=[info.model_dump(include={"name", "name_ko", "category", "description_brief", "filename"}) for info in info_list],
            embeddings=[emb.tolist() for emb in name_embeddings]
        )

    def get_card_image_info(self, id: str)->CardImageInfo:
        return self.__card_info_dict[id]

    def __query_result_to_info_list(self, query_result) -> list[list[tuple[CardImageInfo, float]]]:
        list_length = len(query_result["ids"])

        result = []
        for i in range(list_length):
            if len(query_result["ids"][i]) > 0:
                objs = [self.__card_info_dict[id] for id in query_result["ids"][i]]
                distances = [s for s in query_result["distances"][i]]
                result.append([(o,d) for o,d in zip(objs, distances)])
            else:
                result.append([])
        
        return result


    async def query_nearest_card_image_infos(self, card_infos: list[CardInfo])->list[list[CardImageInfo]]:
        t_start = perf_counter()

        names = [c.label for c in card_infos]
        localized_nm_names = [normalize_korean(c.label_localized) for c in card_infos]

        name_result_dict: dict[str, list[CardImageInfo]|None] = {name:None for name in names}

        #Find exact match of Korean labels.

        localized_name_match_results = self.__card_info_table[self.__card_info_table['name_ko_nm'].isin(localized_nm_names)]
        for id in localized_name_match_results['id'].tolist():
            match = self.__card_info_dict[id]
            if match.name_en not in name_result_dict or name_result_dict[match.name_en] is None:
                name_result_dict[match.name_en] = [match]
            else:
                name_result_dict[match.name_en].append(match)

        #Find exact match of English labels.

        no_name_matched_card_names = [name for name in names if (name not in name_result_dict or name_result_dict[name] is None or len(name_result_dict[name]) == 0)]
        
        name_match_results = self.__collection_name.get(where={"name": {"$in": no_name_matched_card_names}})

        for id in name_match_results["ids"]:
            card_image_info = self.__card_info_dict[id]
            name_result_dict[card_image_info.name_en] = [card_image_info]

        no_name_matched_card_names = [name for name in names if (name not in name_result_dict or name_result_dict[name] is None or len(name_result_dict[name]) == 0)]
        
        print(f"{(len(names) - len(no_name_matched_card_names))} cards directly matched corpus.")
        if len(no_name_matched_card_names) > 0:
            print(f"{len(no_name_matched_card_names)} cards will be matched through vector search...")
            
            name_query = asyncio.to_thread(self.__collection_name.query, query_texts = no_name_matched_card_names, n_results = 1)
            desc_query = asyncio.to_thread(self.__collection_desc.query, query_texts = no_name_matched_card_names, n_results = 1)
            
            name_query_results, desc_query_results = await asyncio.gather(name_query, desc_query)

            #name_query_results = self.__collection_name.query(
            #    query_texts=no_name_matched_card_names,
            #    n_results=1
            #)
            name_query_results = self.__query_result_to_info_list(name_query_results)


            #desc_query_results = self.__collection_desc.query(
            #    query_texts=no_name_matched_card_names,
            #    n_results=1
            #)
            desc_query_results = self.__query_result_to_info_list(desc_query_results)


            for i, name in enumerate(no_name_matched_card_names):
                if name_query_results[i][0][1] < 0.5:
                    name_result_dict[name] = [name_query_results[i][0][0]]
                    print(f"Name win - {name} => {name_result_dict[name][0].filename}")
                else:
                    name_result_dict[name] = [desc_query_results[i][0][0]]
                    print(f"Description win - {name} => {name_result_dict[name][0].filename}")
                      
            result = [name_result_dict[name] for name in names]  
        
        t_end = perf_counter()
        print(f"Card retrieval took {t_end - t_start} sec.")

        return result