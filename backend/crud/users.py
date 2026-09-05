#根据用户名查询用户
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.models.users import User, UserToken
from backend.schemas.users import Register, UserUpdateRequest
from backend.utils import auth


async def get_user_by_username(db: AsyncSession,username:str):
    stmt = select(User).where(User.username == username)
    res =await db.execute(stmt)
    return res.scalar_one_or_none()

#创建用户
async def create_user(db:AsyncSession,userdata:Register):
    #先给密码加密--再add
    hash_password=auth.get_hash_password(userdata.password)
    user =User(username=userdata.username, password=hash_password)
    db.add(user)
    await db.commit()
    await db.refresh(user) #从数据库更新返回最新user
    return user

#生产token
async def create_token(db:AsyncSession,user_id:int):
    #先去生成token+设置过期时间-查询数据库当前用户是否Token

    token=str(uuid.uuid4())
    expires_at=datetime.now()+timedelta(days=7)

    query = select(UserToken).where(UserToken.user_id == user_id)
    res =await db.execute(query)
    user_token=res.scalar_one_or_none()
    if user_token:
        user_token.token=token#更新token
        user_token.expires_at=expires_at#更新创建时间
    else:
        user_token=UserToken(user_id=user_id,token=token,expires_at=expires_at)
        db.add(user_token)
        await db.commit()
    return token

async def authenticate_user(db:AsyncSession,username:str,password:str):
    user = await get_user_by_username(db,username)
    if not user:
        return None
    if not auth.verify_password(password,user.password):
        return None
    return user


#根据token查询用户，验证token-》查询用户
async def get_user_by_token(db:AsyncSession,token:str):
    query =select(UserToken).where(UserToken.token == token)
    token_res = await db.execute(query)
    db_token = token_res.scalar_one_or_none()

    if not db_token or db_token.expires_at < datetime.now():
        return None

    query=select(User).where(User.id==db_token.user_id)
    user_res = await db.execute(query)
    return user_res.scalar_one_or_none()

async def update_user(db:AsyncSession,username:str,user_data:UserUpdateRequest):
    #user_data是一个Pydantic类型，得到字典-》**解包
    #没有设置值的不更新
    query=update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_none=True,
        exclude_unset=True
    ))
    res = await db.execute(query)
    await db.commit()
    #检查更新
    if res.rowcount ==0:
        raise HTTPException(status_code=404, detail="User not found")
    #获取更新后的用户
    updated_user = await get_user_by_username(db,username)
    return updated_user

async def change_password(db:AsyncSession,username:str,old_password:str,new_password:str,user:User):
    if not auth.verify_password(old_password,user.password):
        return False
    if old_password ==new_password:
        raise HTTPException(status_code=400,detail="新密码不能与旧密码一样")
    hashed_new_password = auth.get_hash_password(new_password)
    query = update(User).where(User.username==username).values(password=hashed_new_password)
    res = await db.execute(query)
    await db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=400,detail="密码修改失败")
    return True