# Repository structure

## Root directory

---

### `alembic/`

Contains all *alembic* related configuration. Of special interest is the `alembic/versions` folder, where the migration scripts are located (info on how to add a new revision in [Database migrations](./migrations.md)).

### `docs/`

Contains technical documentation of this repository.

### `k8s/`

Contains *kubernetes* manifests. Used for deployment on *Okteto cloud*, along with the `okteto.yml` manifest.

## `src` directory

---

Contains all source code of the project, including tests.

### `main.py`

The main entrypoint of the app. It contains some general purpose endpoints, like *OpenAPI* docs and `/health`, along with the *CORS* Middleware.

### `auth.py`

User authentication primitives. These are used in API endpoints to validate users.

### `logging.py`

Function wrappers for python's *logging* module.

### `api/`

API-related code. It contains:

* `model/`: *Pydantic* models received by the API
* `trainings.py`: router and endpoints related to trainings
* `trainings_test.py`: tests for the aforementioned endpoints

### `db/`

Database interaction related code. It contains:

* `model/`: *ORM* models used by *SQLAlchemy*
* `migration.py`: code for performing migrations using *alembic*
* `trainings.py`: function wrappers for interacting with the database

### `common/`

Common code extracted from `api` and `db`.

### `metrics/`

Code for interacting with the metrics queue.
