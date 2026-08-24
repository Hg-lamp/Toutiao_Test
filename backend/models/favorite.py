from datetime import datetime

from sqlalchemy import UniqueConstraint, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Integer, DateTime

from backend.models import Base
from backend.models.news import News
from backend.models.users import User


class Favorite(Base):
    __tablename__ = 'favorite'

    #创建索引
    #UniqueConstraint唯一约束，当前用户，当前新闻只能收藏一次
    __table_args__=(
        UniqueConstraint('user_id','news_id',name='user_news_unique'),
        Index('fx_favorite_user_idx','user_id'),
        Index('fx_favorite_news_idx','news_id'),
    )

    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True,comment="收藏id")
    user_id:Mapped[int]=mapped_column(Integer,ForeignKey(User.id),nullable=False,comment="用户id")
    news_id:Mapped[int]=mapped_column(Integer,ForeignKey(News.id),nullable=False,comment="新闻id")
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,nullable=False,comment="创建时间")

    def __repr__(self):
        return f"<favorite{self.id} {self.user_id} {self.news_id}>"