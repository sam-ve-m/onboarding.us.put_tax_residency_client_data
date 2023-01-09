import pickle
from typing import Union

from decouple import config

from func.src.domain.exceptions.model import InternalServerError
from func.src.infrastructures.redis.infrastructure import RedisInfrastructure


class CacheRepository(RedisInfrastructure):
    redis_host = config("REDIS_HOST_URL")
    redis_db = config("REDIS_CACHE_DB")
    prefix = "jormungandr:"

    @classmethod
    async def set(cls, key: str, value: dict, ttl: int = 0):
        """ttl in secounds"""
        redis = cls.get_redis()
        key = f"{cls.prefix}{key}"
        if ttl > 0:
            await redis.set(name=key, value=pickle.dumps(value), ex=ttl)
        else:
            await redis.set(name=key, value=pickle.dumps(value))

    @classmethod
    async def get(cls, key: str) -> Union[dict, str, bytes]:
        redis = cls.get_redis()
        if type(key) != str:
            raise InternalServerError("cache.error.key")
        key = f"{cls.prefix}{key}"
        value = await redis.get(name=key)
        return value and pickle.loads(value) or value
