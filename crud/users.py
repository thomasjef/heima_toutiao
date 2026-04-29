import uuid
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest, UserUpdatePasswordRequest
from utils import security
from datetime import datetime, timedelta

from utils.security import verify_password


# 查询用户
async def get_user_by_username(
        db: AsyncSession,
        username: str
):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 创建用户
async def create_user(
        db: AsyncSession,
        user_data: UserRequest
):
    # 密码加密
    hashed_password = security.get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)  # 从数据库读回最新的user 信息
    return user


# 生成token
async def create_token(
        db: AsyncSession,
        user_id: int
):
    # 生成token + 设置过期时间 + 查询数据当前是否有token，有token, 更新，没有添加
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    # 如果存在，更新，如果不存在，新增
    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    # 找不到用户名
    if not user:
        return None
    # 找到了用户名，密码不对
    if not verify_password(password, user.password):
        return None
    return user


# 根据token查询用户
async def get_user_by_token(db: AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()

    if not db_token or db_token.expires_at < datetime.now():
        return None

    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    # 没有设置值的不更新
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    ))
    result = await db.execute(query)
    await db.commit()

    #检查更新
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    #获取一下更新后的用户
    updated_user = await  get_user_by_username(db, username)
    return updated_user


async def update_password(db: AsyncSession, user: User, password_data: UserUpdatePasswordRequest):
    #先进行旧密码校验
    if not security.verify_password(password_data.old_password, user.password):
        return False
    hashed_new_password = security.get_hash_password(password_data.new_password)
    user.password = hashed_new_password
    db.add(user) #需要加一句add，以防session过期的时候提交不到数据库
    await db.commit()
    await db.refresh(user)
    return True

