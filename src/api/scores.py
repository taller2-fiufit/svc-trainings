from http import HTTPStatus
from fastapi import APIRouter

from src.api.aliases import SessionDep, UserDep
from src.api.model.training import ScoreBody
import src.db.trainings as trainings_db


router = APIRouter(
    prefix="/{id}/scores",
    tags=["Scores"],
)


@router.get("/me", status_code=HTTPStatus.OK)
async def get_score_me(
    session: SessionDep, user: UserDep, id: int
) -> ScoreBody:
    """Get your score for the training"""
    return await trainings_db.get_score(session, id, user.sub)


@router.post("", status_code=HTTPStatus.CREATED)
async def post_score(
    session: SessionDep, user: UserDep, id: int, score: ScoreBody
) -> ScoreBody:
    """Create or update a score"""
    return await trainings_db.add_score(session, id, user.sub, score)
