from typing import Annotated, Callable, List, Optional, Union, Literal

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession


from src.api.model.training import (
    BlockStatus,
    CreateTraining,
    PatchTraining,
    Training,
)
from src.auth import User, get_admin, get_user
from src.db.utils import get_session
import src.db.trainings as trainings_db
from src.metrics.reports import get_reporter


router = APIRouter(
    prefix="/trainings",
    tags=["trainings"],
    dependencies=[Depends(get_session), Depends(get_user), Depends(get_admin)],
)


@router.get("")
async def get_all_trainings(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_user)],
    offset: int = 0,
    limit: int = 100,
    author: Optional[Union[Literal["me"], int]] = None,
) -> List[Training]:
    """Get all trainings"""
    if author is None:
        return await trainings_db.get_all_trainings(session, offset, limit)

    u = user.sub if author == "me" else author
    return await trainings_db.get_all_trainings(session, offset, limit, u)


@router.get("/{id}")
async def get_training(
    id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_user)],
) -> Training:
    """Get the training with the specified id"""
    return await trainings_db.get_training_by_id(session, id)


@router.post("", status_code=201)
async def post_training(
    training: CreateTraining,
    session: Annotated[AsyncSession, Depends(get_session)],
    report_creation: Annotated[
        Callable[[Training], None], Depends(get_reporter)
    ],
    user: Annotated[User, Depends(get_user)],
) -> Training:
    """Create a new training"""
    new_training = await trainings_db.create_training(
        session, user.sub, training
    )
    report_creation(new_training)
    return new_training


@router.patch("/{id}")
async def patch_training(
    id: int,
    training_patch: PatchTraining,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_user)],
) -> Training:
    """Edit training's attributes"""
    return await trainings_db.patch_training(
        session, user.sub, id, training_patch
    )


@router.patch("/{id}/blocked")
async def block_training(
    id: int,
    block_status: BlockStatus,
    session: Annotated[AsyncSession, Depends(get_session)],
    admin: Annotated[User, Depends(get_admin)],
) -> Training:
    """Change training's blocked status"""
    return await trainings_db.change_block_status(
        session, id, block_status.blocked
    )
