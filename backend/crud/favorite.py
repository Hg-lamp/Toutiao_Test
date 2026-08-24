from fastapi import HTTPException
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.favorite import Favorite
from backend.models.news import News


async def is_news_favorite(db:AsyncSession,user_id:int,news_id:int):
    stmt = select(Favorite).where(Favorite.user_id == user_id,Favorite.news_id == news_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none() is not None

async def add_favorite_tool(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    #检查是否收藏过了
    find_is_favorite=await is_news_favorite(db,user_id,news_id)
    if find_is_favorite:
        raise HTTPException(status_code=400,detail="收藏过了，不需要重复收藏")
    favor = Favorite(user_id=user_id,news_id=news_id)
    db.add(favor)
    await db.commit()
    await db.refresh(favor)
    return favor

async def remove_my_favorite_news(db:AsyncSession,user_id:int,news_id:int):
    stmt=delete(Favorite).where(Favorite.news_id==news_id,Favorite.user_id==user_id)
    res =await db.execute(stmt)
    await db.commit()
    return res.rowcount > 0

async def get_my_favorite_list(
        db:AsyncSession,
        user_id:int,
        page:int,
        page_size:int
):
    #总量-收藏的新闻列表
    count_query=select(func.count(Favorite.news_id)).where(Favorite.user_id==user_id)
    count_res = await db.execute(count_query)
    total=count_res.scalar_one()
    #获取收藏列表-联表查询join
    offset=(page-1)*page_size

    query = (
             #查询News表的所有字段和收藏表的创建时间和id
             select(News,Favorite.created_at.label("favorite_time"),Favorite.id.label("favorite_id")).
             #限定返回条件，只返回两个表都匹配的记录
             join(Favorite,Favorite.news_id==News.id).
             #查询保证是当前用户的用户收藏
             where(Favorite.user_id==user_id).
             #按照收藏时间倒序排序
             order_by(Favorite.created_at.desc()).
             #翻页，跳过前面多少条
             offset(offset).
             #限定每页最多返回多少条
             limit(page_size)
             )
    result = await db.execute(query)
    res = result.all()
    return res,total

#清空收藏列表：清空当前用户的
async def clear_all_favorite_news(
        db:AsyncSession,
        user_id:int
):
    stmt = delete(Favorite).where(Favorite.user_id==user_id)
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount