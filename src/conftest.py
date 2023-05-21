import pytest
import asyncio
from httpx import AsyncClient
from typing import AsyncGenerator, Generator
from http import HTTPStatus

from src.auth import get_admin, get_user, ignore_auth
from src.db.migration import downgrade_db
from src.main import app, lifespan
from src.metrics.reports import get_reporter
from src.common.model import TrainingType
from src.api.model.training import (
    CreateTraining,
    Goal,
    Multimedia,
    Training,
)
from src.test_utils import assert_score_is


# https://stackoverflow.com/questions/71925980/cannot-perform-operation-another-operation-is-in-progress-in-pytest
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ---------------
# COMMON FIXTURES
# ---------------


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    # reset database
    await downgrade_db()

    # https://fastapi.tiangolo.com/advanced/testing-dependencies/
    app.dependency_overrides[get_user] = ignore_auth
    app.dependency_overrides[get_admin] = ignore_auth

    def stub_reporter(_: Training) -> None:
        pass

    app.dependency_overrides[get_reporter] = lambda: stub_reporter

    async with lifespan(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client


# -----------------
# TRAINING FIXTURES
# -----------------


@pytest.fixture
async def check_empty_trainings(client: AsyncClient) -> None:
    response = await client.get("/trainings")

    assert response.status_code == HTTPStatus.OK

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
        goals=[Goal(name="goal_1", description="a _veeery_ long description")],
    )

    response = await client.post("/trainings", json=body.dict())

    assert response.status_code == HTTPStatus.CREATED

    result = CreateTraining(**response.json())

    assert result == body

    return Training(**response.json())


# --------------
# SCORE FIXTURES
# --------------


@pytest.fixture
async def scored_training(
    created_body: Training, client: AsyncClient
) -> Training:
    score = 2.3
    response = await client.post(
        f"/trainings/{created_body.id}/scores", json={"score": score}
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {"score": score}

    await assert_score_is(client, score, 1, created_body.id)

    created_body.score = score
    created_body.score_amount = 1

    return created_body


# -----------------
# FAVORITE FIXTURES
# -----------------


@pytest.fixture
async def check_empty_favorites(client: AsyncClient) -> None:
    response = await client.get("/favorites")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.fixture
async def favorited_training(
    created_body: Training, check_empty_favorites: None, client: AsyncClient
) -> Training:
    json = {"training_id": created_body.id}
    response = await client.post("/favorites", json=json)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == json

    return created_body
