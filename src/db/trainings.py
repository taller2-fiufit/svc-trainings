from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.model.training import CreateTraining, PatchTraining, Training
from src.db.model.training import DBTraining


async def get_all_trainings(session: AsyncSession) -> List[Training]:
    res = await session.scalars(select(DBTraining).offset(0).limit(100))
    trainings = res.all()

    return list(map(DBTraining.to_api_model, trainings))


async def get_training_by_id(
    session: AsyncSession, id: int
) -> Optional[Training]:
    training = await session.get(DBTraining, id)
    return None if training is None else training.to_api_model()


async def create_training(
    session: AsyncSession, author: int, training: CreateTraining
) -> Training:
    new_training = DBTraining.from_api_model(author, training)

    async with session.begin():
        session.add(new_training)

    return new_training.to_api_model()


async def patch_training(
    session: AsyncSession, author: int, id: int, training_patch: PatchTraining
) -> Optional[Training]:
    """Updates the training's info"""
    async with session.begin():
        training = await session.get(DBTraining, id)

        if training is None:
            return None

        # TODO: maybe handle this differently
        if training.author != author:
            return None

        training.update(**training_patch.dict())

        session.add(training)

    return training.to_api_model()
