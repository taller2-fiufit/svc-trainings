from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession


from src.api.model.training import CreateTraining, PatchTraining, Training
from src.auth import User, get_user
from src.db.utils import get_session
import src.db.trainings as trainings_db


router = APIRouter(
    prefix="/trainings",
    tags=["trainings"],
    dependencies=[Depends(get_session), Depends(get_user)],
)


@router.get("")
async def get_all_trainings(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_user)],
) -> List[Training]:
    """Get all trainings"""
    return await trainings_db.get_all_trainings(session)


@router.get("/{id}")
async def get_training(
    id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_user)],
) -> Training:
    """Get the training with the specified id"""
    training = await trainings_db.get_training_by_id(session, id)

    if training is None:
        raise HTTPException(404, "Resource not found")

    return training


@router.post("", status_code=201)
async def post_training(
    training: CreateTraining,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_user)],
) -> Training:
    """Create a new training"""
    return await trainings_db.create_training(session, training)


@router.patch("/{id}")
async def patch_training(
    id: int,
    training_patch: PatchTraining,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_user)],
) -> Training:
    """Create a new training"""
    training = await trainings_db.patch_training(session, id, training_patch)

    if training is None:
        raise HTTPException(404, "Resource not found")

    return training


@router.delete("/{id}")
async def delete_training(
    id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_user)],
) -> None:
    """Create a new training"""
    await trainings_db.delete_training(session, id)
