import json

from langchain_core.messages import AIMessageChunk


#流式返回数据
async def stream_response(output):
    async for chunk, metadata in output:
        # 只流 AI 的文本回复，跳过工具执行结果
        if isinstance(chunk, AIMessageChunk) and chunk.content:
            yield f"data: {json.dumps({'content': chunk.content})}\n\n"
    yield "data: [DONE]\n\n"