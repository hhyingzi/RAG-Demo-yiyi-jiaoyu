# 当我们需要定义索引和查询引擎时，会调用此文件。它加载 创建的现有 Milvus 集合，创建索引，并定义查询引擎。
import logging
import os
import pymilvus

from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex
)
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.postprocessor.cohere_rerank import CohereRerank

load_dotenv(".env.example")

def get_index_and_query_engine():

    model = os.getenv("MODEL", "gpt-3.5-turbo")
    llm=OpenAI(model=model)

    cohere_api_key = os.environ["COHERE_API_KEY"]
    cohere_rerank = CohereRerank(api_key=cohere_api_key, top_n=2) # 从重排器返回前 2 个节点

    try:
        milvus_uri = os.getenv("MILVUS_URI")
        milvus_api_key = os.getenv("MILVUS_API_KEY")
        milvus_collection = os.getenv("MILVUS_COLLECTION")
        milvus_dim = os.getenv("MILVUS_DIMENSION")

        if not all([milvus_uri, milvus_api_key, milvus_collection]):
            raise ValueError("Missing required environment variables.")
    
        # 加载现有的集合
        vector_store = MilvusVectorStore(
            uri=milvus_uri,
            token=milvus_api_key,
            collection_name=milvus_collection,
            dim=milvus_dim,
            overwrite=False,
        )

        index = VectorStoreIndex.from_vector_store(vector_store)

        query_engine = index.as_query_engine(
            similarity_top_k=2,
            llm=llm,
            # 目标键默认设置为 window，以匹配 node_parser 的默认设置
            node_postprocessors=[
                MetadataReplacementPostProcessor(target_metadata_key="window"),
                cohere_rerank
            ],
        )

    except (KeyError, ValueError) as e:
        raise ValueError(f"Invalid environment variables: {e}")
    except ConnectionError as e:
        raise ConnectionError(f"Failed to connect to Milvus: {e}")

    return query_engine
