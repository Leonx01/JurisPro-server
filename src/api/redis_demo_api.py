from fastapi import APIRouter
from fastapi import Depends

from src.utils.dependencies import get_redis

router = APIRouter(prefix="/cache", tags=["Cache"])


@router.get("/get")
async def cache_example(key: str, redis_client=Depends(get_redis)):
    value = redis_client.get(key)  # 从 Redis 获取缓存值
    return {"key": key, "value": value}


@router.get("/set")
async def set_cache(key: str, value: str, redis_client=Depends(get_redis)):
    redis_client.setex(key, 60, value)  # 设置 key，60 秒后过期
    return {"message": f"Set {key} successfully"}
