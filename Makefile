.PHONY: install lint format test run dev db-up db-down migrate

install:
	poetry install

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

test:
	poetry run pytest -s -x --cov=app -vv

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev:
	poetry run uvicorn app.main:app --reload

db-up:
	poetry run alembic upgrade head

db-migration:
	poetry run alembic revision --autogenerate -m "$(msg)"

typecheck:
	poetry run mypy .

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down
