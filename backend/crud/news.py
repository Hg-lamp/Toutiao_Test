from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.news import Category, News


async def get_categories(db:AsyncSession,skip:int=0,limit:int=100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()



async def get_news_list(db:AsyncSession,category_id:int=0,limit:int=10,skip:int=0):
    stmt= select(News).where(News.category_id==category_id).offset(skip).limit(limit)
    result=await db.execute(stmt)
    return result.scalars().all()

async def get_new_count(db:AsyncSession,category_id:int):
    stmt =select(func.count(News.id)).where(News.category_id==category_id)
    result  = await db.execute(stmt)
    return result.scalar_one()

async def get_news_detail(db:AsyncSession,news_id:int):
    stmt=select(News).where(News.id==news_id)
    result =await db.execute(stmt)
    return result.scalar_one_or_none()


#实现新闻浏览量的更新
async def increase_news_views(db:AsyncSession,news_id:int):
    stmt=update(News).where(News.id==news_id).values(views=News.views+1)
    res = await db.execute(stmt)
    await db.commit()
#虽然在路由层判断过了，但是一个方法可能被多个业务使用，写入数据库判断，来避免其他业务的缺判断
#更新，检查数据库是否真的命中数据
    return res.rowcount >0


#获取新闻页的同类新闻
async def get_related_news(db:AsyncSession,news_id:int,category_id:int):
    stmt=(select(News).
          where(News.id!=news_id and News.category_id==category_id).
          order_by(News.views.desc()).
          limit(5))
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    return[
        {"id":news_detail.id,
            "title":news_detail.title,
            "content":news_detail.content,
            "image":news_detail.image,
            "author":news_detail.author,
            "publish_time":news_detail.publish_time,
            "category_id":news_detail.category_id,
            "views":news_detail.views,
         } for news_detail in related_news]