from http import HTTPStatus
from typing import Callable, List, Annotated

from fastapi import APIRouter, Depends


from src.api.model.training import (
    BlockStatus,
    CreateTraining,
    FilterParams,
    PatchTraining,
    Training,
)
from src.api.aliases import SessionDep, UserDep
from src.auth import get_admin, get_user
from src.db.utils import get_session
from src.logging import info
import src.db.trainings as trainings_db
from src.metrics.reports import get_training_creation_reporter


router = APIRouter(
    prefix="/trainings",
    tags=["Trainings"],
    # List of dependencies that get run ALWAYS for router and subrouters.
    # For a single-route dependency use the route decorator's parameter "dependencies"
    dependencies=[Depends(get_session), Depends(get_user)],
)

Filters = Annotated[FilterParams, Depends()]
CreationReporterDep = Annotated[
    Callable[[Training], None], Depends(get_training_creation_reporter)
]


@router.get("")
async def get_all_trainings(
    session: SessionDep,
    user: UserDep,
    f: Filters,
) -> List[Training]:
    """Get all trainings"""
    sub = user.sub if f.author == "me" else f.author
    blk = f.blocked if f.blocked != "all" else None
    type = f.type if f.type != "all" else None
    return await trainings_db.get_all_trainings(
        session,
        f.offset,
        f.limit,
        f.mindiff,
        f.maxdiff,
        blk,
        user=sub,
        type=type,
    )


@router.get("/{id}")
async def get_training(session: SessionDep, id: int) -> Training:
    """Get the training with the specified id"""
    return await trainings_db.get_training_by_id(session, id)


@router.post("", status_code=HTTPStatus.CREATED)
async def post_training(
    session: SessionDep,
    user: UserDep,
    report_created: CreationReporterDep,
    training: CreateTraining,
) -> Training:
    """Create a new training"""
    new_training = await trainings_db.create_training(
        session, user.sub, training
    )
    info(f"New training created: {new_training}")
    report_created(new_training)
    return new_training


@router.patch("/{id}")
async def patch_training(
    session: SessionDep,
    user: UserDep,
    id: int,
    training_patch: PatchTraining,
) -> Training:
    """Edit training's attributes"""
    edited_training = await trainings_db.patch_training(
        session, user.sub, id, training_patch
    )
    info(f"Training edited: {edited_training}")
    return edited_training


@router.patch("/{id}/status", dependencies=[Depends(get_admin)])
async def block_training(
    session: SessionDep,
    id: int,
    block_status: BlockStatus,
) -> Training:
    """Change training's blocked status"""
    edited_training = await trainings_db.change_block_status(
        session, id, block_status.blocked
    )
    status = "blocked" if edited_training.blocked else "unblocked"
    info(
        f"Training block status changed. ID: {edited_training.id}"
        f"  Current status: {status}"
    )
    return edited_training


# ----------
# Subrouting
# ----------


def add_subrouters(router: APIRouter) -> None:
    """Set up subrouters"""
    from src.api.scores import router as scores_router

    router.include_router(scores_router)


add_subrouters(router)
