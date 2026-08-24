from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from backend.schemas.base import NewsItemResponse


class FavoriteCheckResponse(BaseModel):
    is_Favorite: bool = Field(...,alias="isFavorite")

class FavoriteAdd(BaseModel):
    news_id:int = Field(...,alias="newsId")

#规划两个类：一个新闻模型类，收藏的模型类
class FavoriteNewsItemResponse(NewsItemResponse):
    favorite_id:int =Field(...,alias="favoriteId")
    favorite_time:datetime=Field(alias="favoriteTime")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
#收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    list:list[FavoriteNewsItemResponse]
    total:int
    has_more:bool=Field(...,alias="hasMore")
    model_config=ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )