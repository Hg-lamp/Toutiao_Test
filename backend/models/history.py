from datetime import datetime

from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, DateTime

from backend.models import Base
from backend.models.news import News
from backend.models.users import User


class History(Base):
    """浏览历史"""
    __tablename__ = 'history'

    __table_args__ = (
        UniqueConstraint('user_id', 'news_id', name='unique_user_news'),
        Index('hx_user_idx', 'user_id'),
        Index('hx_news_idx', 'news_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="浏览历史id")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey(News.id), nullable=False, comment="新闻id")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=True, comment="用户id")
    view_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="新闻查看时间")