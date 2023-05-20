import pytest
from typing import Any, AsyncGenerator, Dict
from httpx import AsyncClient
from http import HTTPStatus

from src.auth import get_admin, get_user, ignore_auth
from src.db.migration import downgrade_db
from src.common.model import TrainingType
from src.api.model.training import (
    BlockStatus,
    CreateTraining,
    Goal,
    Multimedia,
    PatchTraining,
    Training,
)
from src.main import app, lifespan
from src.metrics.reports import get_reporter


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


@pytest.fixture
async def check_empty(client: AsyncClient) -> None:
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


async def test_trainings_get_empty(check_empty: None) -> None:
    # NOTE: all checks are located inside the check_empty fixture
    pass


async def test_trainings_get_nonexistent(client: AsyncClient) -> None:
    response = await client.get("/trainings/1")

    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_trainings_post(created_body: Training) -> None:
    # NOTE: all checks are located inside the created_body fixture
    pass


async def test_trainings_post_no_body(client: AsyncClient) -> None:
    response = await client.post("/trainings")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_trainings_post_duplicated_title(
    created_body: Training, client: AsyncClient
) -> None:
    body = CreateTraining(**created_body.dict())
    response = await client.post("/trainings", json=body.dict())

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": f'A training with the title "{body.title}" already exists'
    }


async def test_trainings_post_get(
    check_empty: None, created_body: Training, client: AsyncClient
) -> None:
    response = await client.get("/trainings")
    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert len(json) == 1

    got = Training(**json[0])

    assert got == created_body

    response = await client.get(f"/trainings/{got.id}")
    assert response.status_code == HTTPStatus.OK
    assert got == Training(**response.json())


async def test_trainings_block(
    created_body: Training, client: AsyncClient
) -> None:
    assert not created_body.blocked

    response = await client.patch(
        f"/trainings/{created_body.id}/status",
        json=BlockStatus(blocked=True).dict(),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["blocked"]


async def test_trainings_patch(
    created_body: Training, client: AsyncClient
) -> None:
    created_body.description = "new description"
    created_body.type = TrainingType.WALK
    body = PatchTraining(**created_body.dict())

    response = await client.patch(
        f"/trainings/{created_body.id}", json=body.dict()
    )
    assert response.status_code == HTTPStatus.OK

    got = Training(**response.json())

    assert got == created_body

    response = await client.get(f"/trainings/{got.id}")
    assert response.status_code == HTTPStatus.OK
    assert got == Training(**response.json())


async def test_filter_trainings(
    created_body: Training, client: AsyncClient
) -> None:
    created_body.blocked = True
    block_status = BlockStatus(blocked=True)
    response = await client.patch(
        f"/trainings/{created_body.id}/status", json=block_status.dict()
    )
    assert response.status_code == HTTPStatus.OK

    response = await client.get("/trainings")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 0

    params: Dict[str, Any] = {"blocked": False}
    response = await client.get("/trainings", params=params)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 0

    params["blocked"] = True
    response = await client.get("/trainings", params=params)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1

    params["mindiff"] = created_body.difficulty
    response = await client.get("/trainings", params=params)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1

    assert created_body.difficulty is not None  # for mypy
    params["mindiff"] = created_body.difficulty + 1
    response = await client.get("/trainings", params=params)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 0


async def assert_invalid(body: dict[str, Any], client: AsyncClient) -> None:
    response_post = await client.post("/trainings", json=body)
    assert response_post.status_code

    response_patch = await client.patch("/trainings/1", json=body)
    assert response_patch.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


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
    await assert_invalid({**body.dict(), "multimedia": ["url"] * 9}, client)

    # too long multimedia url
    await assert_invalid({**body.dict(), "multimedia": ["a" * 256]}, client)

    # too many goals
    await assert_invalid(
        {**body.dict(), "goals": [{"name": str(i)} for i in range(65)]},
        client,
    )

    # too short/long goal name
    await assert_invalid(
        {**body.dict(), "goals": [{"name": "", "description": ""}]},
        client,
    )
    await assert_invalid(
        {**body.dict(), "goals": [{"name": "a" * 31, "description": ""}]},
        client,
    )

    # too long goal description
    await assert_invalid(
        {**body.dict(), "goals": [{"name": "name", "description": "a" * 301}]},
        client,
    )


# ------
# SCORES
# ------


@pytest.fixture
async def scored_training(
    created_body: Training, client: AsyncClient
) -> Training:
    score = 2
    response = await client.post(
        f"/trainings/{created_body.id}/scores", json={"score": score}
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {"score": score}

    await assert_score_is(client, score, 1, created_body.id)

    response = await client.get(f"/trainings/{created_body.id}")

    created_body.score = score
    created_body.score_amount = 1

    return created_body


async def assert_score_is(
    client: AsyncClient, score: int, score_amount: int, training_id: int
) -> None:
    response = await client.get(f"/trainings/{training_id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["score"] == score
    assert response.json()["score_amount"] == score_amount


async def test_post_score(
    scored_training: Training, client: AsyncClient
) -> None:
    # NOTE: all checks are located inside the posted_score fixture
    pass


async def test_edit_score(
    scored_training: Training, client: AsyncClient
) -> None:
    new_score = (int(scored_training.score) + 1) % 5
    response = await client.post(
        f"/trainings/{scored_training.id}/scores",
        json={"score": new_score},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {"score": new_score}

    await assert_score_is(client, new_score, 1, scored_training.id)
