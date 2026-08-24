from fastapi import APIRouter
from starlette.responses import StreamingResponse

from backend.agent.agent_graph import ai_response
from backend.schemas.aichatRes import UserChatRequest
from backend.services.streamresponse import stream_response, change_message

router=APIRouter(prefix="/api/ai",tags=["chat"])


#使用伪流式实现打字机效果
@router.post('/chat')
async def chat(request_body:UserChatRequest):
    res = await ai_response(user_question=request_body.messages[-1].content,user_chat_all=change_message(request_body.messages))
    return StreamingResponse(stream_response(res), media_type="text/event-stream")