from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import os
import uuid
import aiofiles

from backend.config.db_config import get_db
from backend.crud import users
from backend.models.users import User
from backend.schemas.users import UserAuthResponse, UserInfoResponse, Register, UserUpdateRequest, ExchangeUserPassword
from backend.utils.auth import get_current_user
from backend.utils.response import success_response

router = APIRouter(prefix='/api/user',tags=['users'])

@router.post('/register')
async def register(user_data: Register,db:AsyncSession=Depends(get_db)):
    #注册逻辑：验证用户是否存在->创建用户->生成token->响应结果
    existing_user=await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400,detail='该用户已经存在')

    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)
    # return{
    #     "code":200,
    #     "message":"success",
    #     "data":{
    #         "token":token,
    #         "userinfo":{
    #             "id":user.id,
    #             "username":user.username,
    #             "bio":user.bio,
    #             "avatar":user.avatar
    #         }
    #     }
    # }
    response_data=UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功",data=response_data)

@router.post('/login')
async def login(user_data: Register,db:AsyncSession=Depends(get_db)):
    #登录逻辑-》验证用户是否存在-》验证密码-》生成token-》响应结果
    user = await users.authenticate_user(db,user_data.username,user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Incorrect username or password')
    token = await users.create_token(db, user.id)
    response_data=UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功",data=response_data)


#查token查用户-》封装crud-》功能整合成一个工具函数-
@router.get('/info')
def get_user_info(user = Depends(get_current_user)):
    return success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(user))


#修改用户信息，验证token->更新（用户输入数据put提交->请求体参数->定义Pydantic模型类->响应结果）
#参数：用户输入的+验证token +db（调用更新方法）
@router.put('/update')
async def update_user_info(user_data:UserUpdateRequest,user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    user = await users.update_user(db,user.username,user_data)
    return success_response(message="更新用户信息成功",data = UserInfoResponse.model_validate(user))

@router.put('/password')
async def update_password(password_data:ExchangeUserPassword,db:AsyncSession=Depends(get_db),user:User=Depends(get_current_user)):
    res_change_pwd = await users.change_password(db,user.username,password_data.oldPassword,password_data.newPassword,user)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="修改密码失败")
    return success_response(message="密码修改成功")

# 上传头像
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "avatars")

@router.post('/avatar')
async def upload_avatar(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        file: UploadFile = File(...)
):
    # 验证文件类型
    if file.content_type not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        raise HTTPException(status_code=400, detail="只支持 JPG/PNG/GIF/WebP 格式")

    # 生成唯一文件名
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # 保存文件
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    # 更新数据库 avatar 字段
    avatar_url = f"/uploads/avatars/{filename}"
    await users.update_user(db, user.username, UserUpdateRequest(avatar=avatar_url))

    return success_response(message="头像上传成功", data={"avatar": avatar_url})
