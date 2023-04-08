from typing import AsyncGenerator
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


async def test_trainings_get_empty() -> None:
    client = await setup_subjects()

    response = client.get("/trainings/")

    assert response.status_code == 200

    json = response.json()

    assert json == []


async def test_trainings_get_nonexistent() -> None:
    client = await setup_subjects()

    response = client.get("/trainings/1")

    assert response.status_code == 404


async def test_trainings_post() -> None:
    client = await setup_subjects()

    body = CreateTraining(
        title="title",
        description="description",
        type=TrainingType.WALK,
        difficulty=1,
    )

    response = client.post("/trainings/", json=body.dict())

    assert response.status_code == 200


async def test_trainings_post_get() -> None:
    client = await setup_subjects()

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
    assert response.status_code == 200

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
