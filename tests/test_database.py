from sqlalchemy.exc import OperationalError

from app import database


def test_missing_database_url_is_not_ready(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    database.get_engine.cache_clear()
    assert not database.database_ready()
    database.get_engine.cache_clear()


def test_database_engine_failure_is_not_ready(monkeypatch):
    class BrokenEngine:
        def connect(self):
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    monkeypatch.setattr(database, "get_engine", lambda: BrokenEngine())
    assert not database.database_ready()
