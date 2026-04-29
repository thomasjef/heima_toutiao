from pydantic import Field, BaseModel, ConfigDict  # 新闻模型类
from datetime import datetime
from typing import Optional


class NewsItemBase(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int = Field(..., alias="categoryId")
    views: int
    publish_time: Optional[datetime] = Field(..., alias="publishTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )
