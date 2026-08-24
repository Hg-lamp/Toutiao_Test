

from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.db_config import get_db
from backend.crud.history import add_history, get_history_list, delete_my_news_history, clear_all_my_history
from backend.models.users import User
from backend.schemas.history import HistoryAddRequest, HistoryAddResponse, HistoryListResponse
from backend.utils.auth import get_current_user
from backend.utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


#添加新闻查看历史记录
@router.post('/add')
async def add_news_history(
        data:HistoryAddRequest,
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    history = await add_history(db=db,news_id=data.news_id,user_id=user.id)
    return success_response(message="添加历史记录成功",data=HistoryAddResponse.model_validate(history))


@router.get('/list')
async def list_news_history(
        db:AsyncSession=Depends(get_db),
        user:User=Depends(get_current_user),
        page:int=Query(1,ge=1,alias="page"),
        page_size:int=Query(default=10,ge=10,le=20,alias="pageSize")
):
    list_res,total = await get_history_list(db=db,user_id=user.id,page=page,page_size=page_size)
    history_list=[]
    #从返回结果拆分得到每一个历史记录对象的字典
    for news,view_time,history_id in list_res:
        news_dict= {k:v for k,v in news.__dict__.items() if not k.startswith('_')}
        news_dict["view_time"]=view_time
        news_dict["id"]=history_id
        history_list.append(news_dict)

    has_more=total>page*page_size
    return success_response(message="返回浏览历史列表",data=HistoryListResponse(
        list=history_list,
        total=total,
        hasMore=has_more,
    ))

@router.delete('/delete/{history_id}')
async def delete_news_history(
        db:AsyncSession=Depends(get_db),
        user:User=Depends(get_current_user),
        history_id:int=Path(...,ge=1)
):
    res = await delete_my_news_history(db=db,history_id=history_id,user_id=user.id)
    if not res:
        raise HTTPException(status_code=404,detail="没能正确删除该新闻历史")
    return success_response(message="删除历史成功",data=None)


@router.delete('/clear')
async def clear_news_history(
        db:AsyncSession=Depends(get_db),
        user:User=Depends(get_current_user),
):
    res = await clear_all_my_history(db=db,user_id=user.id)
    if not res:
        raise HTTPException(status_code=404,detail="未能正常删除所有历史")
    return success_response(message="历史记录清空成功",data=None)