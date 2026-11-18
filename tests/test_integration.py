import os

import pytest
from fastapi.testclient import TestClient

from app.database import get_engine
from app.main import app


@pytest.mark.integration
def test_postgres_ready_from_real_connection(monkeypatch):
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is not configured")
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_engine.cache_clear()
    try:
        response = TestClient(app).get("/ready")
        assert response.status_code == 200
        assert response.json()["database"] == "connected"
    finally:
        get_engine.cache_clear()
