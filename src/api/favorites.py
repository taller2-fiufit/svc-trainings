from http import HTTPStatus
from typing import Annotated, Callable, List
from fastapi import APIRouter, Depends

from src.api.aliases import SessionDep, UserDep
from src.api.model.favorites import FavoriteRequest
from src.api.model.training import Training
from src.auth import get_user
from src.db.utils import get_session
import src.db.favorites as favorites_db
from src.logging import info
from src.metrics.reports import get_training_favorited_reporter


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
    dependencies=[Depends(get_session), Depends(get_user)],
)

FavoritedReporterDep = Annotated[
    Callable[[int, int], None], Depends(get_training_favorited_reporter)
]


@router.get("")
async def get_favorites(
    session: SessionDep, user: UserDep, offset: int = 0, limit: int = 100
) -> List[Training]:
    """Get all your favorited trainings"""
    return await favorites_db.get_favorites(session, offset, limit, user.sub)


@router.post("", status_code=HTTPStatus.CREATED)
async def favorite(
    session: SessionDep,
    user: UserDep,
    report_favorited: FavoritedReporterDep,
    favorite: FavoriteRequest,
) -> FavoriteRequest:
    """Favorite this training"""
    await favorites_db.favorite(session, user.sub, favorite.training_id)
    info(f"User {user.sub} favorited training {favorite.training_id}")
    report_favorited(user.sub, favorite.training_id)
    return favorite


@router.delete("/{training_id}")
async def unfavorite(
    session: SessionDep, user: UserDep, training_id: int
) -> FavoriteRequest:
    """Un-favorite this training"""
    await favorites_db.unfavorite(session, user.sub, training_id)
    info(f"User {user.sub} un-favorited training {training_id}")
    return FavoriteRequest(training_id=training_id)
