from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import Category, News
from cache.news_cache import get_cached_categories, set_cache_categories, get_cache_news_list, set_cache_news_list
from schemas.base import NewsItemBase


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 先尝试从缓存中获取数据
    cache_categories = await get_cached_categories()
    if cache_categories:
        return cache_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    categories = result.scalars().all()  # orm结果

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)
        await set_cache_categories(categories)

    # 返回数据
    return categories


# 后端查询不用page,直接在controller层面计算出skip值
async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    # 从缓存获取
    page = skip // limit + 1
    cache_list = await get_cache_news_list(category_id, page, limit)
    if cache_list:
        # 需要返回orm格式
        return [News(**item) for item in cache_list]

    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    # 写入缓存
    if news_list:
        # news_data = jsonable_encoder(news_list)
        # 先把orm格式的数据转为字典， prm专程pydantic， 再转成字典
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]
        await set_cache_news_list(category_id, page, limit, news_data)

    return news_list


# 获取新闻分类的总数
async def get_news_count(db: AsyncSession, category_id: int):
    stmt = select(func.count()).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()  # 只能有一个结果，否则报错


# 获取新闻详情
async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 浏览量加1
async def update_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    # session的提交和单条数的提交
    await db.commit()
    # 数据库的更新操作，检查数据库是否真的命中数据
    return result.rowcount > 0


# 相关新闻
async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    # 按照浏览量和发布时间倒序排序，取前5名
    stmt = select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    related_news = result.scalars().all()
    # 列表推导式
    return [{"id": news.id,
             "title": news.title,
             "content": news.content,
             "image": news.image,
             "author": news.author,
             "categoryId": news.category_id,
             "views": news.views
             } for news in related_news]
