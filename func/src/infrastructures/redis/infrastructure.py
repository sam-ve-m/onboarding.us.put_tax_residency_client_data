import aioredis


class RedisInfrastructure:
    redis = None
    redis_host = None
    redis_db = None

    @classmethod
    def get_redis(cls):
        if cls.redis is None:
            url = f"{cls.redis_host}?db={cls.redis_db}"
            cls.redis = aioredis.from_url(url)
        return cls.redis
