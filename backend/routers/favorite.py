from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.db_config import get_db
from backend.crud.favorite import is_news_favorite, add_favorite_tool, remove_my_favorite_news, get_my_favorite_list, \
    clear_all_favorite_news
from backend.models.users import User
from backend.schemas.favorite import FavoriteCheckResponse, FavoriteAdd, FavoriteListResponse
from backend.utils.auth import get_current_user
from backend.utils.response import success_response

router = APIRouter(prefix='/api/favorite',tags=['favorite'])

@router.get('/check')
async def check_favorite(
        news_id:int=Query(...,alias='newsId'),
        user:User = Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
    ):
    is_favorite = await is_news_favorite(news_id=news_id,user_id=user.id,db=db)
    return success_response(message="检查收藏状态成功",data=FavoriteCheckResponse(isFavorite=is_favorite))

#添加收藏
@router.post('/add')
async def add_favorite(data: FavoriteAdd,
                       user:User=Depends(get_current_user),
                       db:AsyncSession=Depends(get_db)):
    res=await add_favorite_tool(db=db,user_id=user.id,news_id=data.news_id)
    return success_response(message="收藏添加成功",data=res)

@router.delete('/remove')
async def remove_favorite(
        news_id:int=Query(...,alias='newsId'),
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    res = await remove_my_favorite_news(db=db,user_id=user.id,news_id=news_id)
    if not res:
        raise HTTPException(status_code=404,detail = "记录删除不存在")
    return success_response(message="删除成功",data=None)

@router.get('/list')
async def get_favorites_list(
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db),
        page:int =Query(default=1,ge=1,alias='page'),
        page_size:int=Query(default=10,ge=10,le=20,alias='page_size'),
):
    rows,total = await get_my_favorite_list(db=db,user_id=user.id,page = page,page_size=page_size)
    favorite_list=[]
    for news,favorite_time,favorite_id in rows:
        news_dict = {k: v for k, v in news.__dict__.items() if not k.startswith('_sa')}
        news_dict['category'] = news_dict.pop('category_id', None)
        news_dict['favorite_time'] = favorite_time
        news_dict['favorite_id'] = favorite_id
        favorite_list.append(news_dict)
    has_more=total>page*page_size
    return success_response(
        message="获取收藏列表成功",
        data=FavoriteListResponse(
            total=total,
            has_more=has_more,
            list=favorite_list
        )
    )

@router.delete('/clear')
async def clear_favorite(db:AsyncSession=Depends(get_db),user: User=Depends(get_current_user)):
    res = await clear_all_favorite_news(db=db,user_id=user.id)
    return success_response(message=f"清空记录{res}",data=None)