from mysql.connector import pooling
from typing import Optional
from os import environ as env

_pool: Optional[pooling.MySQLConnectionPool] = None

get_schema = lambda: env["DB_NAME"]


def get_pool() -> pooling.MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_size=10,
            pool_name="webapp",
            pool_reset_session=True,
            host=env.get("DB_HOST", "localhost"),
            port=int(env.get("DB_PORT", "3306")),
            user=env["DB_USER"],
            password=env["DB_PASSWORD"],
            database=get_schema(),
        )

    return _pool
