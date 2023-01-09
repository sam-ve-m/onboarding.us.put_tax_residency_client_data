from hashlib import sha1

from func.src.repositories.base_repositories.oracle.base import OracleBaseRepository
from func.src.repositories.cache.repository import CacheRepository


class SinacorTypesRepository(OracleBaseRepository):
    cache = CacheRepository

    @classmethod
    async def query_with_cache(cls, sql: str) -> list:
        _sha1 = sha1()
        _sha1.update(str(sql).encode())
        partial_key = _sha1.hexdigest()
        key = f"sinacor_types:{partial_key}"
        value = await cls.cache.get(key=key)
        if not value:
            partial_value = await cls.query(sql=sql)
            value = {"value": partial_value}
            await cls.cache.set(key=key, value=value, ttl=3600)

        value = value.get("value")
        return value

    @classmethod
    async def base_validator(cls, sql: str) -> bool:
        value = await cls.query_with_cache(sql=sql)
        return len(value) >= 1 and value[0][0] == 1

    @classmethod
    async def validate_country(cls, value: str) -> bool:
        sql = f"""
            SELECT 1
            FROM CORRWIN.TSCPAIS
            WHERE SG_PAIS = '{value}'
        """
        return await cls.base_validator(sql=sql)
