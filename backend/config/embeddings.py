import os
from langchain_ollama import OllamaEmbeddings

# 嵌入模型
embed_model = OllamaEmbeddings(
    model="qwen3-embedding:0.6b",
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)