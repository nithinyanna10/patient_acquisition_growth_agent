.PHONY: up down logs api-logs migrate seed

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

api-logs:
	docker compose logs -f api

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python scripts/seed_db.py
