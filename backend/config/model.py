import os

from langchain_community.embeddings import OllamaEmbeddings
from langchain_deepseek import ChatDeepSeek

from backend.schemas.aichatRes import ReflectionResponse
from backend.services.tools import TOOLS

# 聊天大模型
chat_model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.5,
    max_tokens=1024,
    max_retries=2,
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量读取
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
)
# 绑定工具的模型
tool_model = chat_model.bind_tools(TOOLS)
# 结构化规范输出的模型
structured_model = chat_model.with_structured_output(ReflectionResponse)

# 嵌入模型
embed_model = OllamaEmbeddings(
    model="qwen3-embedding:0.6b",
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)