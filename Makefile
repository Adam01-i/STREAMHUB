.PHONY: dev up down migrate test lint

dev:
	uvicorn app.main:app --reload

up:
	docker compose up -d

down:
	docker compose down

migrate:
	alembic upgrade head

test:
	pytest

lint:
	ruff check app tests
	mypy app