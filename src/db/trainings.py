from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.model.training import CreateTraining, Training
from src.db.model.training import DBTraining


async def get_all_trainings(session: AsyncSession) -> List[Training]:
    res = await session.scalars(select(DBTraining).offset(0).limit(100))
    trainings = res.all()

    return list(map(Training.from_orm, trainings))


async def get_training_by_id(
    session: AsyncSession, id: int
) -> Optional[Training]:
    training = await session.get(DBTraining, id)
    return None if training is None else Training.from_orm(training)


async def create_training(
    session: AsyncSession, training: CreateTraining
) -> Training:
    new_training = DBTraining(**training.dict())

    async with session.begin():
        session.add(new_training)

    return Training.from_orm(new_training)
