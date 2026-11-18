"""Small PostgreSQL readiness probe with a cached, pooled SQLAlchemy engine."""

import logging
import os
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_engine():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL is not configured")
    return create_engine(url, pool_pre_ping=True, pool_timeout=2,
                         connect_args={"connect_timeout": 3} if url.startswith("postgresql") else {})


def database_ready() -> bool:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except (SQLAlchemyError, OSError, ValueError):
        logger.warning("Database readiness probe failed")
        return False
