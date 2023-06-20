from typing import Any, Dict
from httpx import AsyncClient
from http import HTTPStatus


from src.common.model import TrainingType
from src.api.model.training import (
    BlockStatus,
    CreateTraining,
    PatchTraining,
    Training,
)


async def test_trainings_get_empty(check_empty_trainings: None) -> None:
    # NOTE: all checks are located inside the check_empty_trainings fixture
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
    check_empty_trainings: None, created_body: Training, client: AsyncClient
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

    response = await client.get("/trainings/count")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"count": 1}


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

    params["blocked"] = "all"
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
    assert response_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

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
