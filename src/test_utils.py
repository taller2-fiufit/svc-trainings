from httpx import AsyncClient
from http import HTTPStatus


async def assert_returns_empty(client: AsyncClient, url: str) -> None:
    response = await client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


async def assert_score_is(
    client: AsyncClient, score: float, score_amount: int, training_id: int
) -> None:
    response = await client.get(f"/trainings/{training_id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["score"] == score
    assert response.json()["score_amount"] == score_amount
