from http import HTTPStatus
from httpx import AsyncClient

from src.api.model.training import (
    Training,
)


async def test_empty_favorites(check_empty_favorites: None) -> None:
    # NOTE: all checks are located inside the check_empty_favorites fixture
    pass


async def test_favorite_training(favorited_training: Training) -> None:
    # NOTE: all checks are located inside the favorited_training fixture
    pass


async def test_get_favorite(
    favorited_training: Training, client: AsyncClient
) -> None:
    response = await client.get("/favorites")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == favorited_training.id
