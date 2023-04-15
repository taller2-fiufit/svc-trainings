from typing import AsyncGenerator, Awaitable, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from src.auth import get_user, ignore_auth
from src.db.model.base import Base
from src.db.model.training import TrainingType
from src.db.mock_session import TestSessionLocal, engine
from src.api.model.training import CreateTraining
from src.main import app
from src.db.utils import get_session


async def setup_subjects() -> TestClient:
    async with engine.begin() as conn:
        # This resets test database
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async def get_mock_session() -> AsyncGenerator[AsyncSession, None]:
        async with TestSessionLocal() as session:
            yield session

    # https://fastapi.tiangolo.com/advanced/testing-dependencies/
    app.dependency_overrides[get_session] = get_mock_session
    app.dependency_overrides[get_user] = ignore_auth

    return TestClient(app)


def with_client(
    test: Callable[[TestClient], Awaitable[None]]
) -> Callable[[], Awaitable[None]]:
    async def decorated_test() -> None:
        client = await setup_subjects()
        await test(client)

    return decorated_test


@with_client
async def test_trainings_get_empty(client: TestClient) -> None:
    response = client.get("/trainings/")

    assert response.status_code == 200

    json = response.json()

    assert json == []


@with_client
async def test_trainings_get_nonexistent(client: TestClient) -> None:
    response = client.get("/trainings/1")

    assert response.status_code == 404


@with_client
async def test_trainings_post(client: TestClient) -> None:
    body = CreateTraining(
        title="title",
        description="description",
        type=TrainingType.WALK,
        difficulty=1,
    )

    response = client.post("/trainings/", json=body.dict())

    assert response.status_code == 201

    result = CreateTraining(**response.json())

    assert result == body


@with_client
async def test_trainings_post_no_body(client: TestClient) -> None:
    response = client.post("/trainings/")
    assert response.status_code == 422


@with_client
async def test_trainings_post_get(client: TestClient) -> None:
    response = client.get("/trainings/")
    assert response.status_code == 200
    assert response.json() == []

    body = CreateTraining(
        title="title",
        description="description",
        type=TrainingType.WALK,
        difficulty=1,
    )
    response = client.post("/trainings/", json=body.dict())
    assert response.status_code == 201

    response = client.get("/trainings/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    got = response.json()[0]

    assert got["title"] == body.title
    assert got["description"] == body.description
    assert got["type"] == body.type
    assert got["difficulty"] == body.difficulty

    response = client.get(f"/trainings/{got['id']}")
    assert response.status_code == 200
    assert got == response.json()


@with_client
async def test_trainings_patch(client: TestClient) -> None:
    body = CreateTraining(
        title="title",
        description="description",
        type=TrainingType.RUNNING,
        difficulty=1,
    )
    response = client.post("/trainings/", json=body.dict())
    assert response.status_code == 201

    body.description = "new description"
    body.type = TrainingType.WALK

    response = client.patch(
        f"/trainings/{response.json()['id']}", json=body.dict()
    )
    assert response.status_code == 200

    got = response.json()

    assert got["title"] == body.title
    assert got["description"] == body.description
    assert got["type"] == body.type
    assert got["difficulty"] == body.difficulty

    response = client.get(f"/trainings/{got['id']}")
    assert response.status_code == 200
    assert got == response.json()


@with_client
async def test_trainings_invalid_body(client: TestClient) -> None:
    # valid body
    body = CreateTraining(
        title="title",
        description="description",
        type=TrainingType.WALK,
        difficulty=1,
    )

    response = client.post("/trainings/", json=body.dict())
    assert response.status_code == 201

    body.title = "other title"

    # too long title
    json = body.dict()
    json["title"] = "a" * 31

    response_post = client.post("/trainings/", json=json)
    response_patch = client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422

    # short title
    json = body.dict()
    json["title"] = ""

    response_post = client.post("/trainings/", json=json)
    response_patch = client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422

    # too long description
    json = body.dict()
    json["description"] = "a" * 301

    response_post = client.post("/trainings/", json=json)
    response_patch = client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422

    # nonexistent type
    json = body.dict()
    json["type"] = "nonexistent type"

    response_post = client.post("/trainings/", json=json)
    response_patch = client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422

    # too high difficulty
    json = body.dict()
    json["difficulty"] = "11"

    response_post = client.post("/trainings/", json=json)
    response_patch = client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422

    # negative difficulty
    json = body.dict()
    json["difficulty"] = "-1"

    response_post = client.post("/trainings/", json=json)
    response_patch = client.patch("/trainings/1", json=json)
    assert response_post.status_code == response_patch.status_code == 422
