#先取代mcp，对工具调用进行统一的，简单的完成
from typing import Any

from langchain_core.messages import ToolMessage

from backend.services.tools import tool_map


class ToolWorker:
    def __init__(self,tool_msg:ToolMessage):
        self.tool_msg = tool_msg


    async def work(self):
        tool_message=[]
        for tool_call in self.tool_msg.tool_calls:
            tool_name = tool_call["name"]
            tool=tool_map[tool_name]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            # 异步调用工具
            content = await tool.ainvoke(tool_args)
            tool_message.append(ToolMessage(content=content,tool_call_id=tool_id))
        return tool_message

    def __repr__(self) -> str:
        return f"<tool_message: {self.tool_msg.content}>工具执行模块"