from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """统一模型基类——所有模型共用这一个 Base，Alembic 才能追踪全部表"""
    pass