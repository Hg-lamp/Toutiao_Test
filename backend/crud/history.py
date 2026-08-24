from datetime import datetime

from sqlalchemy import select, update, func,delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.history import History
from backend.models.news import News


async def add_history(
        news_id:int,
        user_id:int,
        db:AsyncSession,
):
    #先检查历史记录有没有，有则更新时间，无则，添加一条记录
    stmt = select(History).where(History.news_id == news_id, History.user_id == user_id)
    res = await db.execute(stmt)
    result = res.scalar_one_or_none()
    #有记录，更新查看时间
    if result:
        stmt=update(History).where(History.news_id == news_id,History.user_id==user_id).values(view_time=datetime.now())
        new_res=await db.execute(stmt)
        await db.commit()
        await db.refresh(result)
        return result
    history = History(news_id=news_id,user_id=user_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

async def get_history_list(
        db:AsyncSession,
        user_id:int,
        page:int,
        page_size:int,
):
    #统计收藏总量
    stmt = select(func.count(History.news_id)).where(History.user_id == user_id)
    res = await db.execute(stmt)
    total = res.scalar_one()
    #联表查询浏览历史
    query= (select(News,History.view_time.label('viewTime'),History.id.label('history_id')).
            join(History,History.news_id == News.id).
            where(History.user_id == user_id).
            order_by(History.view_time.desc()).
            offset((page-1)*page_size).
            limit(page_size)
            )
    list_res=await db.execute(query)
    final_res = list_res.all()
    return final_res,total

async def delete_my_news_history(
        db:AsyncSession,
        history_id:int,
        user_id:int
):
    stmt=delete(History).where(History.id == history_id,History.user_id == user_id)
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount>0

async def clear_all_my_history(
        db:AsyncSession,
        user_id:int
):
    stmt = delete(History).where(History.user_id == user_id)
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount>0