from typing import List, Optional

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
    query = select(DBFavorite.training)

    if user_id is not None:
        query = query.filter(DBFavorite.user_id == user_id)

    res = await session.scalars(query.offset(offset).limit(limit))
    trainings = res.all()

    return list(map(DBTraining.to_api_model, trainings))
