from langchain_redis import RedisVectorStore

from backend.config.model import embed_model
from backend.config.redis_vector import redis_vector_config

#构建检索器
retriever_database=RedisVectorStore(
    config=redis_vector_config,
    embeddings=embed_model
)
retriever=retriever_database.as_retriever( search_kwargs ={"k":2})