from http import HTTPStatus
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import news
from config.db_conf import get_db
from models.users import User
from utils.auth import get_current_user

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db), skip: int = 0,
                         limit: int = 100):
    # 获取数据库里新闻分类数据
    categories = await news.get_categories(db, skip, limit)
    return {
        "code": HTTPStatus.OK,
        "message": "获取新闻分类成功",
        "data": categories
    }


@router.get("/list")
async def get_news_list(
        db: AsyncSession = Depends(get_db),
        category_id: int = Query(..., alias="categoryId", title="新闻分类id"),
        page: int = Query(1, alias="page", title="页码"),
        page_size: int = Query(10, alias="pageSize", le=100, title="每页数量")
):
    # 处理分页规则
    offset = (page - 1) * page_size
    limit = page_size
    # 查询新闻列表
    news_list = await news.get_news_list(db, category_id, offset, limit)
    # 计算总量
    total = await news.get_news_count(db, category_id)
    # 计算是否还有更多
    hasMore = True if total > offset + len(news_list) else False
    return {
        "code": HTTPStatus.OK,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": hasMore,
        }
    }


@router.get("/detail")
async def get_news_detail(
        db: AsyncSession = Depends(get_db),
        news_id: int = Query(..., alias="id", title="新闻id")
):
    # 获取新闻详情
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="新闻不存在")
    # 浏览量加1
    views_res = await news.update_news_views(db, news_id)
    if not views_res:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="浏览量更新失败")
    # 相关新闻
    related_news = await news.get_related_news(db, news_id, news_detail.category_id)
    return {
        "code": HTTPStatus.OK,
        "message": "获取新闻详情成功",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news,
        }
    }
