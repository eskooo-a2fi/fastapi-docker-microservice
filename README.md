# Dockerized Service Monitor — FastAPI + PostgreSQL + CI/CD

[![Microservice CI](https://github.com/eskooo-a2fi/fastapi-docker-microservice/actions/workflows/main.yml/badge.svg)](https://github.com/eskooo-a2fi/fastapi-docker-microservice/actions/workflows/main.yml)

A deliberately small **full-stack service monitoring demo**: a browser status page, FastAPI backend and PostgreSQL dependency running under Docker Compose. GitHub Actions runs linting, unit tests, a real PostgreSQL integration test and an image build on each push/PR.

**Stack:** Python · FastAPI · SQLAlchemy · PostgreSQL · Docker · Docker Compose · pytest · GitHub Actions (CI/CD) · optional Kubernetes deployment manifest

## Architecture

```text
Browser: GET /, /static/*
           |
           v
FastAPI container (non-root user) ---> GET /health: liveness
           |
           +-------------------------> GET /ready: SQL SELECT 1
                                             |
                                             v
                                      PostgreSQL container
```

The two probes serve different purposes: `GET /health` says the API process is alive, while `GET /ready` returns **503** if the database is down. Both are useful for monitoring, but only readiness verifies the dependency.

## Run with Docker Compose

Install Docker Desktop (or Docker Engine with the Compose plugin). From this folder:

```bash
cp .env.example .env
# Edit .env and change POSTGRES_PASSWORD for local use.
docker compose up --build -d
# Legacy installations may support: docker-compose up --build -d
```

Open **http://localhost:8001** for the status dashboard, or **http://localhost:8001/docs** for the OpenAPI view. The API is published at host port **8001** (container port 8000) to avoid colliding with the RAG app. It is bound only to loopback. PostgreSQL is only accessible from other Compose services, not directly from your laptop.

```bash
curl -i http://localhost:8001/health
# HTTP 200 {"status":"ok","service":"service-monitor"}

curl -i http://localhost:8001/ready
# HTTP 200 {"status":"ready","database":"connected"}
```

Inspect and stop:

```bash
docker compose ps
docker compose logs -f api
docker compose down            # retains database contents in a named volume
# docker compose down --volumes  # deletes the demo database; destructive
```

The `db` service has a `pg_isready` healthcheck; the API starts after the database reports healthy using `depends_on.condition: service_healthy`. The API container runs as non-root, has a Docker healthcheck, and uses one cached SQLAlchemy connection pool. <https://docs.docker.com/compose/how-tos/startup-order/>

## Run the test suite without Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check app tests
pytest -q
```

The database integration test is intentionally skipped without `TEST_DATABASE_URL`. GitHub Actions runs a PostgreSQL service and sets that value, so the real `SELECT 1` path is exercised in CI. It additionally builds the Docker image; **this is CI validation, not automatic production deployment**.

## Failure modes tested

| Scenario | Expected result |
| --- | --- |
| PostgreSQL is down / connection refused | `/ready` returns 503, sanitized message |
| Database is misconfigured / no URL | `/ready` returns 503 |
| Database is down but API stays alive | `/health` still returns 200 |
| Database accepts SQL | `/ready` returns 200 |
| Frontend assets requested | HTML, JS and CSS load |

## Kubernetes extension (illustrative)

`k8s/api.yaml` contains a Deployment and Service with Kubernetes **liveness/readiness probes**, resource limits and secret-based DB configuration. It assumes an existing PostgreSQL instance and a real pushed container image; it is not a full cluster deployment, Helm chart or GitOps setup. Before deploying, replace the image placeholder and create the secret using your own secure workflow. **Do not commit real DB credentials.**

## Limitations / next steps

This is a self-contained demo with no end-user accounts, data models or migrations. Expand it with an Alembic migration, CRUD endpoint, structured logging and OpenTelemetry metrics, persistent monitoring history, and environment-based release deployments. The HTML status page makes this small example full-stack, but it is not a comprehensive product frontend.

## Reference

- [Docker Compose startup order and health checks](https://docs.docker.com/compose/how-tos/startup-order/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
