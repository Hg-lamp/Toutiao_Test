from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Index
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from backend.models import Base


class Conversation(Base):
    __tablename__ = 'conversations'

    #创建索引
    __table_args__ = (
        Index("idx_conversation_id", "id"),
        Index("idx_conversation_user_id", "user_id"),
        Index("idx_thread_id", "conversation_id"),
    )


    #表
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True,comment="会话表id")
    conversation_id:Mapped[str]=mapped_column(String(50),nullable=False,comment="thread_id")
    user_id:Mapped[int]=mapped_column(Integer,nullable=False,comment="user_id")
    title:Mapped[str]=mapped_column(String(50),nullable=False,comment="会话主题")
    message_count:Mapped[int]=mapped_column(Integer,nullable=False,comment="message_count")
    is_expired:Mapped[int]=mapped_column(TINYINT,nullable=False,comment="is_expired")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )