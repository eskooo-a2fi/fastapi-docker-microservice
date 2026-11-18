"""FastAPI health and readiness probes, plus a browser status page."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import database_ready

app = FastAPI(title="Dockerized Service Monitor", version="1.0.0")
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def homepage():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    """Liveness: the API process is running, independent of PostgreSQL."""
    return {"status": "ok", "service": "service-monitor"}


@app.get("/ready")
def ready():
    """Readiness: the API can execute a simple query against PostgreSQL."""
    if not database_ready():
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ready", "database": "connected"}
