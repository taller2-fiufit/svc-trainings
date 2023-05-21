from http import HTTPStatus
from typing import List
from fastapi import APIRouter, Depends

from src.api.aliases import SessionDep, UserDep
from src.api.model.favorites import FavoriteRequest
from src.api.model.training import Training
from src.auth import get_user
from src.db.utils import get_session
import src.db.favorites as favorites_db


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
    dependencies=[Depends(get_session), Depends(get_user)],
)


@router.get("")
async def get_favorites(
    session: SessionDep, user: UserDep, offset: int = 0, limit: int = 100
) -> List[Training]:
    """Get all your favorited trainings"""
    return await favorites_db.get_favorites(session, offset, limit, user.sub)


@router.post("", status_code=HTTPStatus.CREATED)
async def favorite(
    session: SessionDep, user: UserDep, favorite: FavoriteRequest
) -> FavoriteRequest:
    """Favorite this training"""
    await favorites_db.favorite(session, user.sub, favorite.training_id)
    return favorite


@router.delete("")
async def unfavorite(
    session: SessionDep, user: UserDep, favorite: FavoriteRequest
) -> FavoriteRequest:
    """Un-favorite this training"""
    return favorite
