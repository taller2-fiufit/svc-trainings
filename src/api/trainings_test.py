import pytest
from typing import Any, AsyncGenerator
from httpx import AsyncClient

from src.auth import get_user, ignore_auth
from src.db.migration import downgrade_db
from src.common.model import TrainingType
from src.api.model.training import CreateTraining, Goal, Multimedia, Training
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


@pytest.fixture
async def check_empty(client: AsyncClient) -> None:
    response = await client.get("/trainings")

    assert response.status_code == 200

    json = response.json()

    assert json == []


@pytest.fixture
async def created_body(client: AsyncClient) -> Training:
    body = CreateTraining(
        title="title",
        description="description",
        type=TrainingType.WALK,
        difficulty=1,
        multimedia=[Multimedia("image_url"), Multimedia("video_url")],
        goals=[Goal(name="goal_1")],
    )

    response = await client.post("/trainings", json=body.dict())

    assert response.status_code == 201

    result = CreateTraining(**response.json())

    assert result == body

    return Training(**response.json())


async def test_trainings_get_empty(check_empty: None) -> None:
    # NOTE: all checks are located inside the check_empty fixture
    pass


async def test_trainings_get_nonexistent(client: AsyncClient) -> None:
    response = await client.get("/trainings/1")

    assert response.status_code == 404


async def test_trainings_post(created_body: Training) -> None:
    # NOTE: all checks are located inside the created_body fixture
    pass


async def test_trainings_post_no_body(client: AsyncClient) -> None:
    response = await client.post("/trainings")
    assert response.status_code == 422


async def test_trainings_post_get(
    check_empty: None, created_body: Training, client: AsyncClient
) -> None:
    response = await client.get("/trainings")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1

    got = Training(**json[0])

    assert got == created_body

    response = await client.get(f"/trainings/{got.id}")
    assert response.status_code == 200
    assert got == Training(**response.json())


async def test_trainings_patch(
    created_body: Training, client: AsyncClient
) -> None:
    created_body.description = "new description"
    created_body.type = TrainingType.WALK

    response = await client.patch(
        f"/trainings/{created_body.id}", json=created_body.dict()
    )
    assert response.status_code == 200

    got = Training(**response.json())

    assert got == created_body

    response = await client.get(f"/trainings/{got.id}")
    assert response.status_code == 200
    assert got == Training(**response.json())


async def assert_invalid(body: dict[str, Any], client: AsyncClient) -> None:
    response_post = await client.post("/trainings", json=body)
    assert response_post.status_code

    response_patch = await client.patch("/trainings/1", json=body)
    assert response_patch.status_code == 422


async def test_trainings_invalid_body(
    created_body: Training, client: AsyncClient
) -> None:
    body = CreateTraining(**created_body.dict())
    body.title = "other title"

    # NOTE: we edit the dict because the model types contain validations

    # too long title
    await assert_invalid({**body.dict(), "title": "a" * 31}, client)

    # short title
    await assert_invalid({**body.dict(), "title": ""}, client)

    # too long description
    await assert_invalid({**body.dict(), "description": "a" * 301}, client)

    # nonexistent type
    await assert_invalid({**body.dict(), "type": "nonexistent type"}, client)

    # too high difficulty
    await assert_invalid({**body.dict(), "difficulty": "11"}, client)

    # negative difficulty
    await assert_invalid({**body.dict(), "difficulty": "-1"}, client)

    # too many multimedia resources
    await assert_invalid({**body.dict(), "multimedia": ["url"] * 65}, client)

    # too long multimedia url
    await assert_invalid({**body.dict(), "multimedia": ["a" * 256]}, client)

    # too many goals
    await assert_invalid(
        {**body.dict(), "goals": [{"name": str(i)} for i in range(65)]},
        client,
    )

    # too short/long goal name
    await assert_invalid(
        {**body.dict(), "goals": [{"name": ""}]},
        client,
    )
    await assert_invalid(
        {**body.dict(), "goals": [{"name": "a" * 31}]},
        client,
    )
