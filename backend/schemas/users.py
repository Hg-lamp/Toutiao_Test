from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class Register(BaseModel):
    username: str
    password: str


class UserInfoBase(BaseModel):
    """用户信息基础数据模型"""
    nickname:Optional[str]=Field(None,max_length=50,description="昵称")
    avatar:Optional[str]=Field(None,max_length=255,description="头像URL")
    gender:Optional[str]=Field(None,max_length=10,description="性别")
    bio:Optional[str]=Field(None,max_length=500,description="个人简介")
    phone:Optional[str]=Field(None,max_length=11,description="手机号")


#user_info对应的类：基础类+Info类(id,用户名
class UserInfoResponse(UserInfoBase):
    id:int
    username:str
    #模型类配置
    model_config=ConfigDict(
        from_attributes=True,
    )

class UserAuthResponse(BaseModel):
    token:str
    user_info:UserInfoResponse=Field(...,alias="user_info")

    #模型类配置
    model_config = ConfigDict(
        populate_by_name=True,#alias/字段名兼容
        from_attributes=True,#允许从orm对象属性中取值
    )


# 更新用户的模型类
class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50,description="昵称")
    gender:Optional[str] = Field(None,description="性别")
    avatar:Optional[str]= None
    bio:Optional[str]=None
    phone:Optional[str]=None

class ExchangeUserPassword(BaseModel):
    oldPassword:str = Field(...,alias="old_password",description="旧密码")
    newPassword:str = Field(...,min_length=5,alias='new_password',description="新密码")

    model_config = ConfigDict(
        populate_by_name=True,
    )
