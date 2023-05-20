from http import HTTPStatus
from typing import Annotated, Callable, List, Optional, Union, Literal

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession


from src.api.model.training import (
    MAX_DIFFICULTY,
    MIN_DIFFICULTY,
    BlockStatus,
    CreateTraining,
    PatchTraining,
    ScoreBody,
    Training,
)
from src.auth import User, get_admin, get_user
from src.db.utils import get_session
import src.db.trainings as trainings_db
from src.logging import info
from src.metrics.reports import get_reporter


router = APIRouter(
    prefix="/trainings",
    tags=["trainings"],
    # List of dependencies that get run ALWAYS. For a single-route dependency use
    # the route decorator's parameter "dependencies"
    dependencies=[Depends(get_session), Depends(get_user)],
)

SessionDep = Annotated[AsyncSession, Depends(get_session)]
ReporterDep = Annotated[Callable[[Training], None], Depends(get_reporter)]
UserDep = Annotated[User, Depends(get_user)]


@router.get("")
async def get_all_trainings(
    session: SessionDep,
    user: UserDep,
    offset: int = 0,
    limit: int = 100,
    author: Optional[Union[Literal["me"], int]] = None,
    mindiff: int = MIN_DIFFICULTY,
    maxdiff: int = MAX_DIFFICULTY + 1,
) -> List[Training]:
    """Get all trainings"""
    if author is None:
        return await trainings_db.get_all_trainings(
            session, offset, limit, mindiff, maxdiff
        )

    u = user.sub if author == "me" else author
    return await trainings_db.get_all_trainings(
        session, offset, limit, u, mindiff, maxdiff
    )


@router.get("/{id}")
async def get_training(session: SessionDep, id: int) -> Training:
    """Get the training with the specified id"""
    return await trainings_db.get_training_by_id(session, id)


@router.post("", status_code=HTTPStatus.CREATED)
async def post_training(
    session: SessionDep,
    user: UserDep,
    report_creation: ReporterDep,
    training: CreateTraining,
) -> Training:
    """Create a new training"""
    new_training = await trainings_db.create_training(
        session, user.sub, training
    )
    info(f"New training created: {new_training}")
    report_creation(new_training)
    return new_training


@router.patch("/{id}")
async def patch_training(
    session: SessionDep,
    user: UserDep,
    id: int,
    training_patch: PatchTraining,
) -> Training:
    """Edit training's attributes"""
    edited_training = await trainings_db.patch_training(
        session, user.sub, id, training_patch
    )
    info(f"Training edited: {edited_training}")
    return edited_training


@router.patch("/{id}/status", dependencies=[Depends(get_admin)])
async def block_training(
    session: SessionDep,
    id: int,
    block_status: BlockStatus,
) -> Training:
    """Change training's blocked status"""
    edited_training = await trainings_db.change_block_status(
        session, id, block_status.blocked
    )
    status = "blocked" if edited_training.blocked else "unblocked"
    info(
        f"Training block status changed. ID: {edited_training.id}"
        f"  Current status: {status}"
    )
    return edited_training


@router.get("/{id}/scores/me", status_code=HTTPStatus.OK)
async def get_score_me(
    session: SessionDep, user: UserDep, id: int
) -> ScoreBody:
    """Get your score for the training"""
    return await trainings_db.get_score(session, id, user.sub)


@router.post("/{id}/scores", status_code=HTTPStatus.CREATED)
async def post_score(
    session: SessionDep, user: UserDep, id: int, score: ScoreBody
) -> ScoreBody:
    """Create or update a score"""
    print(score)
    await trainings_db.add_score(session, id, user.sub, score.score)
    return score
