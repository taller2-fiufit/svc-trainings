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
	poetry run pytest .

run: install
	LOCAL=1 poetry run uvicorn src.main:app --host 0.0.0.0 --port 8080
