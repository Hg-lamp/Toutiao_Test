import os

from langchain_deepseek import ChatDeepSeek
from backend.services.tools import CHILD_TOOLS, PARENT_TOOLS

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

# 绑定所有工具的父模型
tool_model = chat_model.bind_tools(PARENT_TOOLS)

#绑定除子agent之外的所有工具的子模型
child_model = chat_model.bind_tools(CHILD_TOOLS)