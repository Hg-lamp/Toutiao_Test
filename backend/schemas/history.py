from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from backend.schemas.base import NewsItemResponse


class HistoryAddRequest(BaseModel):
    news_id:int = Field(...,alias="newsId")
    model_config = ConfigDict(
        populate_by_name=True,  # alias/字段名兼容
        from_attributes=True,  # 允许从orm对象属性中取值
    )

class HistoryAddResponse(BaseModel):
    id:int = Field(...,alias="id")
    user_id:int = Field(...,alias="userId")
    news_id:int = Field(...,alias="newsId")
    view_time:datetime=Field(...,alias="viewTime")
    model_config = ConfigDict(
        populate_by_name=True,  # alias/字段名兼容
        from_attributes=True,  # 允许从orm对象属性中取值
    )

class HistoryNewsItemResponse(NewsItemResponse):
    view_time:datetime=Field(...,alias="viewTime")

class HistoryListResponse(BaseModel):
    list:list[HistoryNewsItemResponse]
    total:int =Field(...,alias="total")
    hasMore:bool=Field(...,alias="hasMore")