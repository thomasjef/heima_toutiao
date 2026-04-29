from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


# 检查收藏状态，检查当前用户是否收藏了这一条信息
async def is_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    # 返回布尔值
    return result.scalar_one_or_none() is not None


# 添加收藏
async def add_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    result = Favorite(user_id=user_id, news_id=news_id)
    db.add(result)
    await db.commit()
    await db.refresh(result)
    return result


# 取消收藏
async def remove_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = delete(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id
    )
    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount > 0


#查询收藏列表
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    # 总量 + 收藏的新闻列表
    stmt = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(stmt)
    total = count_result.scalar_one()

    #联表查询获取收藏信息，按照收藏时间排序
    skip = (page - 1) * page_size
    #相同的字段可以使用别名
    query_stmt = select(
        News,
        Favorite.created_at.label("favorite_time"),
        Favorite.id.label("favorite_id")
    ).join(
        Favorite, Favorite.news_id == News.id
    ).where(
        Favorite.user_id == user_id,
    ).order_by(Favorite.created_at.desc()).offset(skip).limit(page_size)
    result = await db.execute(query_stmt)
    rows = result.all()
    return rows, total


#清空收藏列表
async def clear_all_favorite(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


