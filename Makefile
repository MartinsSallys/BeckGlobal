.PHONY: install lint format typecheck test run db-up db-downgrade db-migration docker-up docker-down

install:
	poetry install

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run mypy .

test:
	poetry run pytest -s -x --cov=app -vv

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

db-up:
	poetry run alembic upgrade head

db-downgrade:
	poetry run alembic downgrade -1

db-migration:
	poetry run alembic revision --autogenerate -m "$(msg)"

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down
