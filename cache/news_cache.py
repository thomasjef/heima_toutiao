#新闻相关的缓存方法,新闻分类的读取与写入
from typing import Dict, Any, Optional

from config.cache_conf import get_json_cache, set_cache


CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news_list:"


#获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)


#写入新闻分类缓存
async def set_cache_categories(data: list[Dict[str, Any]], expire: int = 7200 ):
    return await set_cache(CATEGORIES_KEY, data, expire)



#新闻列表写入缓存, key = news_list:分类id:页码：每页数量
async def set_cache_news_list(category_id: Optional[int], page: int, page_size: int, data: list[Dict[str, Any]], expire: int = 1800):
    # 调用封装的redis 的设置方法，存新闻列表到缓存
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{page_size}"
    return await set_cache(key, data, expire)


##新闻列表读取缓存
async def get_cache_news_list(category_id: Optional[int], page: int, page_size: int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{page_size}"
    return await get_json_cache(key)