import json
import uuid

from fastapi import HTTPException
from langchain_core.messages import AIMessageChunk
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user

from backend.agent.agent_graph import ai_response
from backend.config.mysql_config import AsyncSessionLocal
from backend.models.conversations import Conversation
from backend.models.messages import Message
from backend.models.users import User


async def check_thread_id(thread_id:str,user_id:int,db:AsyncSession,question:str):
    #传空意味着这是新会话
    if not thread_id:
        #直接生成一个
        new_id = str(uuid.uuid4())
        #更新conversation表
        db.add(Conversation(conversation_id=new_id,user_id=user_id,title=question[0:50],is_expired=0,message_count=0))
        await db.commit()
        return new_id
    #否则判断会话列表是否存在id
    stmt = select(Conversation).where(Conversation.user_id == user.id,Conversation.conversation_id == thread_id)
    res = await db.execute(stmt)
    res = res.scalar_one_or_none()
    if res is None:
        raise HTTPException(status_code=404, detail="Conversation not exists")
    return thread_id

async def add_message(thread_id:str,content:str,role:str,db:AsyncSession):
    message = Message(conversation_id=thread_id,content=content,role=role)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return True


async def generate(thread_id:str,question:str,user_id:int):
    async with AsyncSessionLocal() as s:  # 独立 session
        #第一次将用户问题存储到消息列表
        await add_message(db=s, thread_id=thread_id, role="user", content=question)
        stmt = update(Conversation).where(Conversation.conversation_id == thread_id,Conversation.user_id == user_id)
        await s.execute(stmt)
        await s.commit()
        full =""
        async for chunk, metadata in ai_response(question, thread_id):
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                full += chunk.content
                yield f"data: {json.dumps({'content': chunk.content})}\n\n"
        #将ai的回答添加到数据库的messages表
        await add_message(db=s, thread_id=thread_id, role="assistant", content=full)  # ③ 流完写 assistant
    yield "data: [DONE]\n\n"