from enum import Enum

from pydantic import BaseModel, Field


class IntentEnum(str, Enum):
    rag ="rag"
    tool="tool"
    llm="llm"
class IntentRequest(BaseModel):
    data:IntentEnum=Field(...,description="对于用户问题的意图识别：宠物相关为rag，信息查询和工具调用为tool，前面两个都不涉及可以直接对问题回答则为llm")