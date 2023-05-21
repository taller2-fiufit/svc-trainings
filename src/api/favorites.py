from http import HTTPStatus
from typing import List
from fastapi import APIRouter

from src.api.aliases import SessionDep, UserDep
from src.api.model.favorites import FavoriteRequest
from src.api.model.training import Training


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
)


@router.get("")
async def get_favorites(session: SessionDep, user: UserDep) -> List[Training]:
    """Get all your favorited trainings"""
    return []


@router.post("", status_code=HTTPStatus.CREATED)
async def favorite(
    session: SessionDep, user: UserDep, favorite: FavoriteRequest
) -> FavoriteRequest:
    """Favorite this training"""
    return favorite


@router.delete("")
async def unfavorite(
    session: SessionDep, user: UserDep, favorite: FavoriteRequest
) -> FavoriteRequest:
    """Un-favorite this training"""
    return favorite
