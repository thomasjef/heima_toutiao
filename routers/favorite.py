from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.users import User
from schemas.favorite import FavoriteCheckResponse
from utils.auth import get_current_user
from config.db_conf import get_db
from utils.response import success_response
from crud import favorite
from schemas.favorite import FavoriteAddResponse, FavoriteAddRequest, FavoriteListResponse

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    检查用户的收藏状态
    :param news_id: 新闻id
    :param user: 用户认证
    :param db: 数据库信息
    """
    is_favorite = await favorite.is_news_favorite(db=db, user_id=user.id, news_id=news_id)
    # is_favorite = await favorite.is_news_favorite(db=db, user_id=5, news_id=news_id)
    return success_response(message="检查收藏状态成功", data=FavoriteCheckResponse(isfavorite=is_favorite))


# 添加收藏
@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await favorite.add_news_favorite(db=db, user_id=user.id, news_id=data.news_id)
    data = FavoriteAddResponse.model_validate(result)
    return success_response(message="添加收藏成功", data=data)


#取消收藏
@router.delete("/remove")
async def remove_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    flag = await favorite.remove_news_favorite(db, user.id, news_id)
    if not flag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏记录不存在")
    return success_response(message="取消收藏成功")


#获取收藏列表
@router.get("/list")
async def get_favorite_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = [{
        **news.__dict__,
        "favorite_time": favorite_time,
        "favorite_id": favorite_id
    } for news, favorite_time, favorite_id in rows]
    has_more = total > page * page_size
    data = FavoriteListResponse(list=favorite_list, total=total, has_more=has_more)
    return success_response(data=data)


#清空收藏列表
@router.delete("/clear")
async def clear_favorite_list(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    delete_count = await favorite.clear_all_favorite(db, user.id)
    return success_response(message="成功删除{}条收藏列表".format(delete_count))