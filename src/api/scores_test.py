from httpx import AsyncClient
from http import HTTPStatus


from src.api.model.training import (
    Training,
)
from src.test_utils import assert_score_is


async def test_post_score(
    scored_training: Training, client: AsyncClient
) -> None:
    # NOTE: all checks are located inside the posted_score fixture
    pass


async def test_edit_score(
    scored_training: Training, client: AsyncClient
) -> None:
    new_score = float((int(scored_training.score) + 2) % 5)
    response = await client.post(
        f"/trainings/{scored_training.id}/scores",
        json={"score": new_score},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {"score": new_score}

    await assert_score_is(client, new_score, 1, scored_training.id)
