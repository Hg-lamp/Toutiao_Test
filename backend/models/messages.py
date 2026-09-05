from datetime import datetime

from sqlalchemy import Index, Integer, String, TEXT, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from backend.models import Base


class Message(Base):
    __tablename__ = "messages"

    __table_args__ = (
        Index('idx_conversation_id', 'conversation_id'),
    )

    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True,comment="id")
    conversation_id:Mapped[str]=mapped_column(String(36),nullable=False,comment="会话id")
    role:Mapped[str]=mapped_column(String(10),comment="会话对象")
    content:Mapped[str]=mapped_column(TEXT,comment="对话内容")
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.now,comment="创建时间")
