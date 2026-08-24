import traceback

from fastapi import HTTPException,Request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status
from starlette.responses import JSONResponse
#开发模式返回详细的错误信息
#生产模式返回简化的错误信息
DEBUG_MODE=True

async def http_exception_handler(request:Request,exc:HTTPException):
    #处理HTTPException异常
    #这个异常通常是业务逻辑主动抛出的，data保持None
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code":exc.status_code,
            "message":exc.detail,
            "data":None
        }
    )



async def integrity_error_handler(request:Request,exc:IntegrityError):
    error_msg=str(exc.orig)
    if "username_UNIQUE" in error_msg or "Duplicate entry" in error_msg:
        detail="用户名已经存在"
    elif "FOREIGN KEY" in error_msg:
        detail="关联数据不存在"
    else:
        detail="数据约束冲突，请检查输入"
    error_data=None
    if DEBUG_MODE:
        error_data={
            "error_type":"IntegrityError",
            "error_detail":error_msg,
            "path":str(request.url)
        }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code":400,
            "message":detail,
            "data":error_data
        }
    )



async def sqlalchemy_error_handler(request:Request,exc:SQLAlchemyError):
    """处理SQLALchemy数据库错误"""
    #开发模式下返回详细错误信息
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type":type(exc).__name__,
            "error_detail":str(exc),
            "traceback":traceback.format_exc(),
            "path":str(request.url)
        }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code":500,
            "message":"数据库操作失败",
            "data":error_data
        }
    )




async def general_exception_handler(request:Request,exc:Exception):
    error_data=None
    if DEBUG_MODE:
        error_data={
            "error_type":type(exc).__name__,
            "error_detail":str(exc),
            #格式化异常信息为字符串，方便日志记录和调试
            "traceback":traceback.format_exc(),
            "path":str(request.url)
        }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code":500,
            "message":"服务器内部出错",
            "data":error_data
        }
    )