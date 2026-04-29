from datetime import datetime

from pydantic import Field, ConfigDict
from pydantic import BaseModel

from schemas import base


#添加浏览记录的模型
class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")

    model_config = ConfigDict(
        populate_by_name=True,  # alias和字段名兼容
        from_attributes=True  # 允许从orm对象属性取值
    )


class HistoryAddResponse(HistoryAddRequest):
    id: int = Field(..., alias="id")
    user_id: int = Field(..., alias="userId")
    view_time: datetime = Field(..., alias="viewTime")

    model_config = ConfigDict(
        populate_by_name=True,  # alias和字段名兼容
        from_attributes=True  # 允许从orm对象属性取值
    )


class HistoryItemResponse(base.NewsItemBase):
    """记录列表项"""
    view_time: datetime = Field(..., alias="viewTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


class HistoryListResponse(BaseModel):
    """返回的列表模型"""
    list: list[HistoryItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,  # alias和字段名兼容
        from_attributes=True  # 允许从orm对象属性取值
    )