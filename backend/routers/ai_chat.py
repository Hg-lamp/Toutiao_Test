from fastapi import APIRouter
from starlette.responses import StreamingResponse

from backend.agent.agent_graph import ai_response
from backend.schemas.aichatRes import UserChatRequest
from backend.services.streamresponse import stream_response


router=APIRouter(prefix="/api/ai",tags=["chat"])


#返回ai生成的结果使用伪流式实现打字机效果
@router.post('/chat')
async def chat(request_body:UserChatRequest):
    res = ai_response(input=request_body.messages[-1].content,thread_id=request_body.thread_id)
    return StreamingResponse(stream_response(res), media_type="text/event-stream")

