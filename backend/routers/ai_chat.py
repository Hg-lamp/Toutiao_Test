from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from backend.config.mysql_config import get_db
from backend.config.upload_config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, MAX_CHARS
from backend.crud.ai_chat import check_thread_id, generate
from backend.models.users import User
from backend.schemas.ai_chat_response import UserChatRequest, UploadResponse
from backend.services.file_parser import parse_content
from backend.utils.auth import get_current_user

router = APIRouter(prefix="/api/ai", tags=["chat"])


# 返回ai生成的结果使用伪流式实现打字机效果
@router.post('/chat')
async def chat(request_body: UserChatRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 检查线程id
    thread_id = await check_thread_id(request_body.thread_id, user.id, db, request_body.messages[-1].content)
    # 流式返回结果
    return StreamingResponse(generate(thread_id=thread_id, question=request_body.messages[-1].content, user_id=user.id),
                             media_type="text/event-stream")


@router.post('/upload', response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """上传文件，解析文本内容后返回，不存盘，供对话上下文注入。"""
    # 1. 校验文件类型
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {ext}，仅支持 {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 2. 读取文件内容（限制大小）
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大（{len(content) / 1024 / 1024:.1f}MB），最大支持 5MB"
        )

    # 3. 根据文件类型解析文本
    try:
        text = parse_content(content, ext)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")

    # 4. 限制文本长度（防止前端炸掉）
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n\n...（文件过长，已截断）"

    return UploadResponse(
        filename=file.filename or "unknown",
        text=text,
        size=len(content),
    )


