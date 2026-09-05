from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.mysql_config import get_db
from backend.crud import news,cache_news

#创建apirouter实例
router = APIRouter(prefix='/api/news',tags=['news'])

#接口实现流程
#1.模块化路由
#2.定义模型类-数据库表
#3.在crud文件里面创建文件，封装操作数据库的方法
#4.在路由处理函数里面调用crud封装好的方法，响应结果

@router.get('/categories')
async def categories(skip:int=0,limit:int=100,db:AsyncSession=Depends(get_db)):
    #获取数据库里面新闻分类数据-先定义模型类-封装查询数据的方法
    categories =await cache_news.get_categories(db, skip, limit)
    return {
        "code":200,
        "message":"获取新闻分类成功",
        "data":categories

    }





@router.get('/list')
async def get_list(
        category_id:int=Query(default=0,alias="categoryId"),
        page:int=1,
        page_size:int=Query(default=10,alias="pageSize"),
        db:AsyncSession=Depends(get_db)
):
    #处理分页规则 查询新闻列表 计算总量 计算是否还有更多
    offset = (page-1)*page_size

    data=await cache_news.get_news_list(db, category_id, page_size, offset)
    total=await news.get_new_count(db, category_id)
    has_more = (offset+len(data))<total
    return{
        "code":200,
        "message":"success",
        "data":{
            "list":data,
            "total":total,
            "has_more":has_more,
        }
    }
@router.get('/detail')
async def get_detail(news_id:int = Query(...,alias="id"),db:AsyncSession=Depends(get_db)):
    #获取新闻详情 + 浏览量+1 + 相关新闻
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404,detail="新闻不存在")
    if not await news.increase_news_views(db, news_detail.id):
        raise HTTPException(status_code=404,detail="新闻不存在")
    related_news= await news.get_related_news(db, news_detail.id, news_detail.category_id)
    return{
        "code":200,
        "message":"success",
        "data":{
            "id":news_detail.id,
            "title":news_detail.title,
            "content":news_detail.content,
            "image":news_detail.image,
            "author":news_detail.author,
            "publish_time":news_detail.publish_time,
            "category_id":news_detail.category_id,
            "views":news_detail.views,
            "relatedNews":related_news
        }
    }
