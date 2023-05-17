from http import HTTPStatus
from typing import List, Optional
from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.model.training import CreateTraining, PatchTraining, Training
from src.db.model.training import DBScore, DBTraining


async def get_all_trainings(
    session: AsyncSession,
    offset: int,
    limit: int,
    mindiff: int,
    maxdiff: int,
    user: Optional[int] = None,
) -> List[Training]:
    query = select(DBTraining)

    if user is not None:
        query = query.filter_by(author=user)

    query = query.filter(
        DBTraining.difficulty >= mindiff, DBTraining.difficulty < maxdiff
    )

    res = await session.scalars(query.offset(offset).limit(limit))
    trainings = res.all()

    return list(map(DBTraining.to_api_model, trainings))


async def get_training_by_id(session: AsyncSession, id: int) -> Training:
    training = await session.get(DBTraining, id)

    if training is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Resource not found")

    return training.to_api_model()


async def check_title_is_unique(session: AsyncSession, title: str) -> None:
    training = await session.scalar(select(DBTraining).filter_by(title=title))
    if training is not None:
        raise HTTPException(
            HTTPStatus.CONFLICT,
            f'A training with the title "{title}" already exists',
        )


async def create_training(
    session: AsyncSession, author: int, training: CreateTraining
) -> Training:
    new_training = DBTraining.from_api_model(author, training)

    async with session.begin():
        await check_title_is_unique(session, training.title)  # type: ignore
        session.add(new_training)

    return new_training.to_api_model()


async def patch_training(
    session: AsyncSession, author: int, id: int, patch: PatchTraining
) -> Training:
    """Updates the training's info"""

    async with session.begin():
        training = await session.get(DBTraining, id)

        if training is None:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Resource not found")

        if patch.title is not None and patch.title != training.title:
            await check_title_is_unique(session, patch.title)

        if training.author != author:
            raise HTTPException(
                HTTPStatus.UNAUTHORIZED, "User isn't author of the training"
            )

        training.update(**patch.dict())

        session.add(training)

    return training.to_api_model()


async def change_block_status(
    session: AsyncSession,
    id: int,
    new_block_status: bool,
) -> Training:
    """Updates the training's info"""
    async with session.begin():
        training = await session.get(DBTraining, id)

        if training is None:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Resource not found")

        training.blocked = new_block_status

        session.add(training)

    return training.to_api_model()


async def add_score(
    session: AsyncSession,
    id: int,
    user: int,
    score: int,
) -> None:
    """Adds a new score to the given training"""
    async with session.begin():
        training = await session.get(DBTraining, id)

        if training is None:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Resource not found")

        new_score = DBScore(training_id=id, author=user, score=score)

        training.scores.append(new_score)

        session.add(training)
