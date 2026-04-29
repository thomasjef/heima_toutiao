from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from schemas import base

# 检查收藏的返回值校验
class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isfavorite")


class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")


# 添加收藏的返回值，直接从orm中获取字段
class FavoriteAddResponse(FavoriteAddRequest):
    id: int
    user_id: int = Field(..., alias="userId")
    created_at: datetime = Field(..., alias="createTime")

    model_config = ConfigDict(
        populate_by_name=True,  # alias和字段名兼容
        from_attributes=True  # 允许从orm对象属性取值
    )

class FavoriteItemResponse(base.NewsItemBase):
    """收藏列表项"""
    favorite_time: datetime = Field(..., alias="favoriteTime")
    favorite_id: int = Field(..., alias="favoriteId")

    model_config = ConfigDict(
        populate_by_name=True,  # alias和字段名兼容
        from_attributes=True  # 允许从orm对象属性取值
    )


# 收藏列表响应的模型类
class FavoriteListResponse(BaseModel):
    """收藏列表"""
    list: list[FavoriteItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,  # alias和字段名兼容
        from_attributes=True  # 允许从orm对象属性取值
    )
