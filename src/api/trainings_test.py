import pytest
from typing import AsyncGenerator
from httpx import AsyncClient

from src.auth import get_user, ignore_auth
from src.db.migration import downgrade_db
from src.db.model.training import TrainingType
from src.api.model.training import CreateTraining
from src.main import app, lifespan
from src.metrics.reports import get_reporter


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    # reset database
    await downgrade_db()

    # https://fastapi.tiangolo.com/advanced/testing-dependencies/
    app.dependency_overrides[get_user] = ignore_auth

    def stub_reporter(_: int) -> None:
        pass

    app.dependency_overrides[get_reporter] = lambda: stub_reporter

    async with lifespan(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client


async def test_trainings_get_empty(client: AsyncClient) -> None:
    response = await client.get("/trainings")

    assert response.status_code == 200

    json = response.json()

    assert json == []


async def test_trainings_get_nonexistent(client: AsyncClient) -> None:
    response = await client.get("/trainings/1")

    assert response.status_code == 404


async def test_trainings_post(client: AsyncClient) -> None:
    body = CreateTraining(
        title="title",
        description="description",
        type=TrainingType.WALK,
        difficulty=1,
    )

    response = await client.post("/trainings", json=body.dict())

    assert response.status_code == 201

    result = CreateTraining(**response.json())

    assert result == body


async def test_trainings_post_no_body(client: AsyncClient) -> None:
    response = await client.post("/trainings")
    assert response.status_code == 422


async def test_trainings_post_get(client: AsyncClient) -> None:
    response = await client.get("/trainings")
    assert response.status_code == 200
    assert response.json() == []

    body = CreateTraining(
        title="title",
        description="description",
        type=TrainingType.WALK,
        difficulty=1,
    )
    response = await client.post("/trainings", json=body.dict())
    assert response.status_code == 201

    response = await client.get("/trainings")
    assert response.status_code == 200
    assert len(response.json()) == 1

    got = response.json()[0]

    assert got["title"] == body.title
    assert got["description"] == body.description
    assert got["type"] == body.type
    assert got["difficulty"] == body.difficulty

    response = await client.get(f"/trainings/{got['id']}")
    assert response.status_code == 200
    assert got == response.json()


async def test_trainings_patch(client: AsyncClient) -> None:
    body = CreateTraining(
        title="title",
        description="description",
        type=TrainingType.RUNNING,
        difficulty=1,
    )
    response = await client.post("/trainings", json=body.dict())
    assert response.status_code == 201

    body.description = "new description"
    body.type = TrainingType.WALK

    response = await client.patch(
        f"/trainings/{response.json()['id']}", json=body.dict()
    )
    assert response.status_code == 200

    got = response.json()

    assert got["title"] == body.title
    assert got["description"] == body.description
    assert got["type"] == body.type
    assert got["difficulty"] == body.difficulty

    response = await client.get(f"/trainings/{got['id']}")
    assert response.status_code == 200
    assert got == response.json()


async def test_trainings_invalid_body(client: AsyncClient) -> None:
    # valid body
    body = CreateTraining(
        title="title",
        description="description",
        type=TrainingType.WALK,
        difficulty=1,
    )

    response = await client.post("/trainings", json=body.dict())
    assert response.status_code == 201

    body.title = "other title"

    # too long title
    json = body.dict()
    json["title"] = "a" * 31

    response_post = await client.post("/trainings", json=json)
    response_patch = await client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422

    # short title
    json = body.dict()
    json["title"] = ""

    response_post = await client.post("/trainings", json=json)
    response_patch = await client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422

    # too long description
    json = body.dict()
    json["description"] = "a" * 301

    response_post = await client.post("/trainings", json=json)
    response_patch = await client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422

    # nonexistent type
    json = body.dict()
    json["type"] = "nonexistent type"

    response_post = await client.post("/trainings", json=json)
    response_patch = await client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422

    # too high difficulty
    json = body.dict()
    json["difficulty"] = "11"

    response_post = await client.post("/trainings", json=json)
    response_patch = await client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422

    # negative difficulty
    json = body.dict()
    json["difficulty"] = "-1"

    response_post = await client.post("/trainings", json=json)
    response_patch = await client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422
