# Patient Acquisition & Growth Agent — Launch Control Center

A delivery management prototype for a hospital AI implementation. Built as a take-home assignment for an AI Solutions Architect role.

The focus is not just building the AI agent. It is delivering it safely — through a real hospital environment, with real compliance gates, real clinical workflows, and real failure modes.

---

## What It Is

An internal launch control system used by a delivery team implementing a "Patient Acquisition & Growth Agent" at Meridian Health System. The tool tracks delivery readiness across seven workstreams over an 8-week implementation and produces a weighted, auditable readiness score rather than a manually set traffic light.

Current state: **64.6% AMBER** — progressing, but two active blockers and one failing go/no-go gate.

---

## Run It (Prototype UI)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

This mode is still available for quick local exploration.

---

## Production-Grade Stack

This repository now includes a deployable backend stack:

- FastAPI service for agent endpoints
- PostgreSQL for persistent state
- SQLAlchemy ORM + Alembic migrations
- Seed pipeline from `data/*.json` into SQL
- Docker Compose orchestration for DB/API/UI
- JWT auth and RBAC (`admin`, `operator`, `viewer`)
- Audit logging for privileged actions
- Agent intelligence APIs (planner, simulator, recommendation memory)
- Notifications queue and CSV export endpoints
- Metrics endpoint (`/metrics`) and background scheduler heartbeat
- Pytest suite + GitHub Actions CI workflow

### Services

- API: `http://localhost:8000`
- API health: `http://localhost:8000/v1/health`
- Growth agent brief endpoint: `http://localhost:8000/v1/agent/brief`
- OpenAPI docs: `http://localhost:8000/docs`
- Prometheus metrics: `http://localhost:8000/metrics`
- Streamlit UI: `http://localhost:8501`

### Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

The API container runs migrations and seeds the database on startup.

Default seeded users:

- `admin@example.com` / `admin123`
- `operator@example.com` / `operator123`
- `viewer@example.com` / `viewer123`

### Run API Locally (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
cd backend
alembic upgrade head
python scripts/seed_db.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Deliverables

| # | Deliverable | Location |
|---|-------------|----------|
| 1 | Delivery operating model | Workstream Health page + `data/workstreams.json` |
| 2 | Milestone / timeline view | Milestone Tracker page + `data/milestones.json` |
| 3 | Dependency and risk view | RAID Log page + `data/raid.json` |
| 4 | Technical-readiness note | `docs/technical_readiness_note.md` |
| 5 | Lightweight coded prototype | This repo — `streamlit run app.py` |
| 6 | Sample client status update | Client Status Update page (generated in-app) |
| 7 | Stakeholder map | `docs/stakeholder_map.md` |
| 8 | Post-launch metrics note | `docs/post_launch_metrics.md` |
| 9 | AI workflow note | Below |

---

## What the Prototype Does

Eight pages, each serving a distinct delivery function:

**Executive Overview** — Weighted readiness score with a launch decision (GO / NO-GO), status drivers, highest-impact actions ranked by score delta, and week-over-week trend.

**Growth Agent Control Tower** — A sophisticated execution copilot that converts readiness signals into a ranked 72-hour action backlog, owner-specific command queues, autonomous escalation triggers, and an operating cadence for steering governance.

**Workstream Health** — Progress across all seven delivery workstreams. At-risk workstreams are dampened in the scoring formula (×0.7); blocked workstreams further (×0.4). This is shown explicitly, not hidden.

**Milestone Tracker** — 12 milestones across 8 weeks with dependency chain tracking. A slipped milestone surfaces warnings on every downstream milestone that depends on it.

**RAID Log** — 18 items across Risks, Issues, Assumptions, and Dependencies. Sorted by severity and urgency. Only open Risks and Issues affect the readiness score — Assumptions and Dependencies are advisory.

**Go / No-Go Checklist** — 15 launch gate criteria across Technical, Clinical Safety, Compliance, Legal, and Operations. A single failure in any critical category blocks launch regardless of overall score.

**Client Status Update** — Generates a structured weekly narrative from live delivery data. Blockers, risks, next-week focus, and decisions needed — ready to send in 60 seconds.

**Scenario Simulator** — Toggle any milestone to Slipped or re-open any resolved risk and watch the score recompute in real time. Shows the exact delta per change.

---

## Readiness Score Formula

| Domain | Weight | Method |
|--------|--------|--------|
| Workstream Health | 30% | Average effective progress (raw % × status multiplier) |
| Milestone Completion | 25% | Weighted average: Complete 1.0, On Track 0.8, At Risk 0.4, Slipped 0.0 |
| RAID Risk Score | 20% | Starts at 100; deducts per open Risk/Issue: Critical −15, High −8, Medium −3 |
| Go/No-Go Readiness | 25% | Pass rate across 15 gate criteria |

**GO threshold: 80%.** Any failure in Compliance, Legal, or Clinical Safety is an automatic NO-GO regardless of score.

---

## Design Decisions That Signal Delivery Thinking

**Transparent weighted scoring.** Not a traffic light a PM sets manually. Weights are documented and auditable. Stakeholders can challenge the model, not just the output.

**Status multipliers on workstream progress.** "90% complete but At Risk" is not the same as "90% complete On Track." The score reflects this — and explains it.

**Dependency cascade.** At-risk milestones that sit in a dependency chain are flagged explicitly. The EHR Credentials slip cascades to EHR UAT, which cascades to Clinical Validation. That chain is visible.

**RAID category discrimination.** Only Risks and Issues penalise the score. Assumptions and Dependencies are tracked but advisory. This matches how an experienced delivery lead actually classifies exposure.

**Critical-fail override.** A Compliance or Legal failure vetoes the numeric score. Reflects real-world go/no-go gate logic.

**Resolution impact analysis.** For every open item, the tool reruns the scoring model with that one change applied. The "+1.6%" next to "Load Testing failure" is not an estimate — it is the formula output.

**Scenario simulator.** Recomputes from first principles on every state change. No cached or hardcoded deltas.

**Action intelligence layer.** The growth agent combines expected score impact with severity, urgency, and launch-blocking status to prioritize intervention sequences, not just report issues.

---

## Project Structure

```
app.py                      # Entry point — page routing, data loading
data/                       # JSON seed data (no database required)
models/                     # Typed dataclasses — Workstream, Milestone, RAIDItem, ChecklistItem
scoring/readiness.py        # All scoring logic — weights, formulas, resolution impact engine
ui/                         # One module per page
utils/helpers.py            # Shared utilities
docs/                       # Standalone delivery documents
backend/                    # Production backend (FastAPI + SQLAlchemy + Alembic)
docker-compose.yml          # Multi-service orchestration (db + api + streamlit)
.github/workflows/          # CI for backend tests
```
