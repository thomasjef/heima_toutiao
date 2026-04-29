from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.db_conf import get_db
from fastapi import Depends

from models.users import User
from schemas.users import UserRequest, UserAuthRespoonse, UserInfoResponse, UserUpdateRequest, UserUpdatePasswordRequest
from crud import users
from utils.response import success_response
from utils.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["user"])

@router.post("/register")
async def register(
        user_data: UserRequest,
        db: AsyncSession = Depends(get_db),
):
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        return {
            "code": HTTPStatus.BAD_REQUEST,
            "message": "用户已存在",
            "data": None
        }
    user = await users.create_user(db, user_data)
    #生成token
    token = await users.create_token(db, user.id)
    # return {
    #     "code": HTTPStatus.OK,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar,
    #         }
    #     }
    # }
    response_data = UserAuthRespoonse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = await users.create_token(db, user.id)
    response_data = UserAuthRespoonse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    #通过token来查询用户信息
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


#修改用户信息，验证token -> 更新(put请求)
@router.put("/update")
async def update_user_info(
        user_data: UserUpdateRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user = await users.update_user(db, user.username, user_data)
    data = UserInfoResponse.model_validate(user)
    return success_response(message="更新用户信息成功", data=data)


#更新密码
@router.put("/password")
async def update_user_password(
        password_data: UserUpdatePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    res_update_password = await users.update_password(db, user, password_data)
    if res_update_password:
        return success_response(message="更新密码成功")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败，请稍后再试")
