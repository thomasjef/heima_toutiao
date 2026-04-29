from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# 用户请求信息
class UserRequest(BaseModel):
    username: str
    password: str


# user_info对应的类
class UserInfoBase(BaseModel):
    """用户信息基础数据模型"""
    nickname:  Optional[str] = Field(None, max_length=50, description="昵称")
    avatar:  Optional[str] = Field(None, max_length=255, description="头像url")
    gender:  Optional[str] = Field(None, max_length=10, description="性别")
    bio:  Optional[str] = Field(None, max_length=500, description="个人简介")


class UserInfoResponse(UserInfoBase):
    """用户信息"""
    id: int
    username: str

    # 模型类配置
    model_config = ConfigDict(
        from_attributes=True  #允许从orm对象属性取值
    )


# data数据类型
class UserAuthRespoonse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")

    # 模型类配置
    model_config = ConfigDict(
        populate_by_name=True, #alias和字段名兼容
        from_attributes=True  #允许从orm对象属性取值
    )


#更新用户信息的模型类
class UserUpdateRequest(BaseModel):
    nickname: str  = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None


#用户密码模型类
class UserUpdatePasswordRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., alias="newPassword", max_length=10, description="新密码")