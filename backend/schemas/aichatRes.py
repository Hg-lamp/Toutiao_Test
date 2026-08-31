from typing import Optional

from pydantic import BaseModel, Field


class MessageItem(BaseModel):
    role:str
    content:str

class UserChatRequest(BaseModel):
    messages: list[MessageItem]
    thread_id:Optional[str]


class ReflectionResponse(BaseModel):
    is_solved:bool = Field(...,description="对用户问题的回答判断是否得以解决用户的问题")
    reason:str =Field(max_length=25,description="对于这个问题的回答是否解决给出原因，简短一句话即可")