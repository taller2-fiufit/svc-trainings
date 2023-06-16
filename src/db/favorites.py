from http import HTTPStatus
from typing import List, Optional
from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.model.training import (
    Training,
)
from src.db.model.favorite import DBFavorite
from src.db.model.training import DBTraining


async def get_favorites(
    session: AsyncSession,
    offset: int,
    limit: int,
    user_id: Optional[int] = None,
) -> List[Training]:
    """Get all the user's favorited trainings"""
    query = select(DBFavorite)

    if user_id is not None:
        query = query.filter(DBFavorite.user_id == user_id)

    res = await session.scalars(query.offset(offset).limit(limit))
    trainings = map(lambda f: f.training, res.all())

    return list(map(DBTraining.to_api_model, trainings))


async def favorite(
    session: AsyncSession, user_id: int, training_id: int
) -> None:
    """Add a training to the user's favorites"""
    training = await session.get(DBTraining, training_id)

    if training is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Training not found")

    favorite = DBFavorite(user_id=user_id, training_id=training_id)

    session.add(favorite)


async def unfavorite(
    session: AsyncSession, user_id: int, training_id: int
) -> None:
    """Add a training to the user's favorites"""
    favorite = await session.scalar(
        select(DBFavorite)
        .filter_by(user_id=user_id, training_id=training_id)
        .limit(1)
    )

    if favorite is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Training's not favorited")

    await session.delete(favorite)
