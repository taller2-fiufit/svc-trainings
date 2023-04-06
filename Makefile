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
