# Production Runbook

## Architecture

- `db` (PostgreSQL 16): durable storage for workstreams, milestones, RAID, and checklist records.
- `api` (FastAPI): exposes `/v1/agent/brief` and health checks, runs migrations and seed on boot.
- `streamlit` (UI): delivery-control interface; can coexist with API-backed workflows.

## Database Lifecycle

1. Migrations are defined in `backend/alembic/versions/`.
2. API startup runs `alembic upgrade head`.
3. Seed job (`backend/scripts/seed_db.py`) upserts initial records from `data/`.

## Operational Commands

```bash
docker compose up --build
docker compose logs -f api
docker compose exec api alembic current
docker compose exec db psql -U postgres -d growth_agent -c "\dt"
```

## Hardening Checklist

- Move default DB credentials to secure secrets manager.
- Add API authentication (JWT or mTLS) before exposing externally.
- Add structured logging and distributed tracing.
- Add CI pipeline with migration checks and contract tests.
- Add backup/restore policy for PostgreSQL volume.
