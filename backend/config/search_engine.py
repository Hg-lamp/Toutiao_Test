import os

from langchain_community.utilities import SearxSearchWrapper

SearXNG = SearxSearchWrapper(
    searx_host=os.getenv("SEARXNG_HOST", "http://localhost:8080"),
    k=3
)