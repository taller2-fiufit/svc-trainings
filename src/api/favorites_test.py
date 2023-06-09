from http import HTTPStatus
from httpx import AsyncClient

from src.api.model.training import (
    Training,
)
from src.test_utils import assert_returns_empty


async def test_empty_favorites(check_empty_favorites: None) -> None:
    # NOTE: all checks are located inside the check_empty_favorites fixture
    pass


async def test_favorite_training(favorited_training: Training) -> None:
    # NOTE: all checks are located inside the favorited_training fixture
    pass


async def test_get_favorite(
    favorited_training: Training, client: AsyncClient
) -> None:
    response = await client.get("/trainings")
    assert response.status_code == HTTPStatus.OK
    all_trainings = response.json()

    response = await client.get("/favorites")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == all_trainings


async def test_delete_favorite(
    favorited_training: Training, client: AsyncClient
) -> None:
    response = await client.delete(f"/favorites/{favorited_training.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"training_id": favorited_training.id}

    await assert_returns_empty(client, "/favorites")

    response = await client.get("/trainings")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
