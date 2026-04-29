import os

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine


# 数据库url
use_docker_flag = os.getenv("USE_DOCKER", "").lower() in {"1", "true", "yes"}
if use_docker_flag:
    ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@mysql:3306/news_app?charset=utf8mb4"
else:
    ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@127.0.0.1:3306/news_app?charset=utf8mb4"

# 创建异步引擎
aysnc_engine = create_async_engine(
    url=ASYNC_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

#创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=aysnc_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

#依赖项,用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
