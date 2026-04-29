from datetime import datetime

from sqlalchemy import select, update, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_history(
        user_id: int,
        news_id: int,
        db: AsyncSession
):
    # 需要先检查是否已经存在该条记录
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    history = result.scalar_one_or_none()
    # 如果能查到记录，则更新时间
    if history:
        updatesql = update(History).where(History.user_id == user_id, History.news_id == news_id).values(
            view_time=datetime.now())
        await db.execute(updatesql)
        await db.commit()
        return history
    # 如果查不到浏览记录，就新增一条记录
    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


# 获取浏览记录
async def get_history_list(
        db: AsyncSession,
        user_id: int = 1,
        page: int = 1,
        page_size: int = 10
):
    # 总量 + 浏览记录列表
    stmt = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(stmt)
    total = count_result.scalar_one()

    # 联表查询获取收藏信息，按照收藏时间排序
    skip = (page - 1) * page_size
    # 相同的字段可以使用别名
    query_stmt = select(
        News,
        History.view_time.label("view_time")
    ).join(
        History, News.id == History.news_id
    ).where(
        History.user_id == user_id,
    ).order_by(
        History.view_time.desc()
    ).offset(skip).limit(page_size)
    result = await db.execute(query_stmt)
    rows = result.all()
    return rows, total



#删除单条浏览记录
async def delete_history(
        history_id: int,
        user_id: int,
        db: AsyncSession,
):
    delete_stmt = delete(History).where(History.news_id == history_id, History.user_id == user_id)
    result = await db.execute(delete_stmt)
    await db.commit()
    return result.rowcount > 0


#清空浏览记录
async def delete_all_history(
        user_id: int,
        db: AsyncSession
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount
