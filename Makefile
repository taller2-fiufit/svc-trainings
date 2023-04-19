all: format lint mypy test

install:
	poetry install

format:
	poetry run black src alembic

lint:
	poetry run flake8 src alembic

mypy:
	poetry run mypy --strict src alembic

test:
	poetry run pytest -sv .
	rm local.db || true

coverage:
	poetry run pytest --cov . --cov-report xml

run: install
	poetry run uvicorn src.main:app --host 0.0.0.0 --port 8080
