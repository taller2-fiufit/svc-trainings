from http import HTTPStatus
from typing import List, Optional
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.model.training import CreateTraining, PatchTraining, Training
from src.db.model.training import DBTraining


async def get_all_trainings(
    session: AsyncSession, offset: int, limit: int, user: Optional[int] = None
) -> List[Training]:
    query = select(DBTraining)

    if user is not None:
        query = query.filter_by(author=user)

    res = await session.scalars(query.offset(offset).limit(limit))
    trainings = res.all()

    return list(map(DBTraining.to_api_model, trainings))


async def get_training_by_id(session: AsyncSession, id: int) -> Training:
    training = await session.get(DBTraining, id)

    if training is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Resource not found")

    return training.to_api_model()


async def create_training(
    session: AsyncSession, author: int, training: CreateTraining
) -> Training:
    new_training = DBTraining.from_api_model(author, training)

    async with session.begin():
        session.add(new_training)

    return new_training.to_api_model()


async def patch_training(
    session: AsyncSession, author: int, id: int, training_patch: PatchTraining
) -> Training:
    """Updates the training's info"""
    async with session.begin():
        training = await session.get(DBTraining, id)

        if training is None:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Resource not found")

        if training.author != author:
            raise HTTPException(
                HTTPStatus.UNAUTHORIZED, "User isn't author of the training"
            )

        training.update(**training_patch.dict())

        session.add(training)

    return training.to_api_model()
