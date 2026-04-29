from fastapi import Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from fastapi import APIRouter
from models.users import User
from utils.auth import get_current_user
from utils.response import success_response

from crud import history
from schemas.history import HistoryAddRequest, HistoryAddResponse, HistoryListResponse

router = APIRouter(prefix="/api/history", tags=["history"])


# 添加历史记录
@router.post("/add")
async def add_history(
        data: HistoryAddRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    history_record = await history.add_history(user.id, data.news_id, db)
    data = HistoryAddResponse.model_validate(history_record)
    return success_response(message="添加成功", data=data)


@router.get("/list")
async def get_history_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    获取用户浏览历史列表
    :param page: 页码
    :param page_size: 页大小
    :param user: 用户认证
    :param db: 数据库信息
    """
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    history_list = [{
        **history_record.__dict__,
        "view_time": view_time
    } for history_record, view_time in rows]
    has_more = total > page * page_size
    data = HistoryListResponse(list=history_list, total=total, has_more=has_more)
    return success_response(data=data)


# 删除单条浏览记录,给过来的history_id其实是news_id
@router.delete("/delete/{history_id}")
async def delete_single_history(
        history_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    flag = await history.delete_history(history_id, user.id, db)
    if not flag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="浏览记录不存在")
    return success_response(message="删除成功")


#清空浏览记录
@router.delete("/clear")
async def clear_history_list(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    delete_count = await history.delete_all_history(user.id, db)
    return success_response(message="成功删除{}条浏览记录".format(delete_count))
