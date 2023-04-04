all: format lint mypy test

install:
	poetry install

format:
	poetry run black .

lint:
	poetry run flake8 src

mypy:
	poetry run mypy --strict .

test:
	poetry run pytest .
