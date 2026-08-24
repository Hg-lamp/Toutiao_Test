import json

from langchain_core.messages import AIMessage, HumanMessage

from backend.schemas.aichatRes import MessageItem


#前端消息列表处理
def change_message(list_msg:list[MessageItem]):
    graph_messages_list=[AIMessage(content=item.content) if item.role=="assistant" else HumanMessage(content = item.content)  for item in list_msg]
    return graph_messages_list

#流式返回数据
async def stream_response(output:str):
    for chunk in output:
        yield f"data: {json.dumps({'content':chunk})}\n\n"
    yield "data: [DONE]\n\n"