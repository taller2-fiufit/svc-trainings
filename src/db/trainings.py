from http import HTTPStatus
from typing import List, Optional
from fastapi import HTTPException

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.model.training import (
    CreateTraining,
    PatchTraining,
    ScoreBody,
    Training,
    TrainingCount,
)
from src.common.model import TrainingType
from src.db.model.training import DBScore, DBTraining


async def get_all_trainings(
    session: AsyncSession,
    offset: int,
    limit: int,
    mindiff: int,
    maxdiff: int,
    blocked: Optional[bool] = None,
    user: Optional[int] = None,
    type: Optional[TrainingType] = None,
) -> List[Training]:
    query = select(DBTraining)

    if blocked is not None:
        query = query.filter_by(blocked=blocked)

    if user is not None:
        query = query.filter_by(author=user)

    if type is not None:
        query = query.filter_by(type=type)

    query = query.filter(
        DBTraining.difficulty >= mindiff, DBTraining.difficulty < maxdiff
    )

    res = await session.scalars(query.offset(offset).limit(limit))
    trainings = res.all()

    return list(map(DBTraining.to_api_model, trainings))


async def count_trainings(
    session: AsyncSession,
    mindiff: int,
    maxdiff: int,
    blocked: Optional[bool] = None,
    user: Optional[int] = None,
    type: Optional[TrainingType] = None,
) -> TrainingCount:
    """Counts the number of services"""
    query = select(func.count()).select_from(DBTraining)

    if blocked is not None:
        query = query.filter_by(blocked=blocked)

    if user is not None:
        query = query.filter_by(author=user)

    if type is not None:
        query = query.filter_by(type=type)

    query = query.filter(
        DBTraining.difficulty >= mindiff, DBTraining.difficulty < maxdiff
    )

    count = (await session.scalar(query)) or 0

    return TrainingCount(count=count)


async def get_training_by_id(session: AsyncSession, id: int) -> Training:
    training = await session.get(DBTraining, id)

    if training is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Training not found")

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

    await check_title_is_unique(session, training.title)  # type: ignore
    session.add(new_training)
    await session.commit()

    return new_training.to_api_model()


async def patch_training(
    session: AsyncSession, author: int, id: int, patch: PatchTraining
) -> Training:
    """Updates the training's info"""

    training = await session.get(DBTraining, id)

    if training is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Training not found")

    if patch.title is not None and patch.title != training.title:
        await check_title_is_unique(session, patch.title)

    if training.author != author:
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, "User isn't author of the training"
        )

    training.update(**patch.dict())

    session.add(training)
    await session.commit()

    return training.to_api_model()


async def change_block_status(
    session: AsyncSession,
    id: int,
    new_block_status: bool,
) -> Training:
    """Updates the training's block status"""
    training = await session.get(DBTraining, id)

    if training is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Training not found")

    training.blocked = new_block_status

    session.add(training)
    await session.commit()

    return training.to_api_model()


async def get_score(
    session: AsyncSession,
    id: int,
    user: int,
) -> ScoreBody:
    """Gets your last score for the training"""
    db_score = await session.scalar(
        select(DBScore).filter_by(training_id=id, author=user).limit(1)
    )

    if db_score is None:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, "Score or training not found"
        )

    return ScoreBody(score=db_score.get_api_score())


async def add_score(
    session: AsyncSession,
    id: int,
    user: int,
    score: ScoreBody,
) -> ScoreBody:
    """Adds a new score to the given training, or edits existing ones"""
    training = await session.get(DBTraining, id)

    if training is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Training not found")

    db_score = await session.scalar(
        select(DBScore).filter_by(training_id=id, author=user).limit(1)
    )

    if db_score is None:
        db_score = DBScore.from_api(id, user, score.score)
    else:
        db_score.update_score(score.score)

    session.add(db_score)
    await session.commit()

    return ScoreBody(score=db_score.get_api_score())
