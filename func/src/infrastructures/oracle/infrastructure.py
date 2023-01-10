from contextlib import asynccontextmanager

import cx_Oracle_async
from decouple import config


class OracleInfrastructure:

    pool = None

    @classmethod
    async def _get_pool(cls):
        if cls.pool is None:
            cls.pool = await cx_Oracle_async.create_pool(
                dsn=config("ORACLE_CONNECTION_STRING"),
                user=config("ORACLE_USER"),
                password=config("ORACLE_PASSWORD"),
                min=2,
                max=100,
                increment=1
            )
        return cls.pool

    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        pool = await cls._get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                yield cursor
                await conn.commit()
