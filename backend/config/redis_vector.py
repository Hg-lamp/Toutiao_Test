import os

from langchain_redis import RedisConfig

redis_vector_config = RedisConfig(
    index_name="index",
    redis_url=os.getenv("REDIS_VECTOR_URL", "redis://localhost:6380"),
    metadata_schema=[
        {"name": "category", "type": "tag"},
        {"name": "num", "type": "numeric"}
    ]
)