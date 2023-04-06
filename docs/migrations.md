# Migrating the database with Alembic

## How to add a database revision

1. create a local database with the latest schema

    ```bash
    $ LOCAL=1 poetry run alembic upgrade head
    ```

2. create a new revision titled _"new revision"_
    ```bash
    $ LOCAL=1 poetry run alembic revision --autogenerate -m "new revision"
    ```

