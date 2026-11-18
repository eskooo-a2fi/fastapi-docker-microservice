from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_health_is_independent_of_database(monkeypatch):
    monkeypatch.setattr(main, "database_ready", lambda: False)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "service-monitor"}


def test_ready_when_database_responds(monkeypatch):
    monkeypatch.setattr(main, "database_ready", lambda: True)
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["database"] == "connected"


def test_ready_returns_503_during_database_outage(monkeypatch):
    monkeypatch.setattr(main, "database_ready", lambda: False)
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.json() == {"detail": "Database unavailable"}


def test_frontend_loads():
    page = client.get("/")
    assert page.status_code == 200
    assert "Service Monitor" in page.text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/styles.css").status_code == 200
