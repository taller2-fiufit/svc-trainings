from src.api.training import CreateTraining, Training
from src.db.model.training import DBTraining

from typing import Annotated, AsyncGenerator, List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    from src.db.session import SessionLocal

    async with SessionLocal() as session:
        yield session


router = APIRouter(
    prefix="/trainings",
    tags=["trainings"],
    dependencies=[Depends(get_session)],
)


@router.get("")
async def get_all_trainings(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> List[Training]:
    """Get all trainings"""
    res = await session.scalars(select(DBTraining).offset(0).limit(100))
    trainings = res.all()

    return list(map(Training.from_orm, trainings))


@router.get("/{id}")
async def get_training(
    id: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> Training:
    """Get the training with the specified id"""
    training = await session.get(DBTraining, id)
    return Training.from_orm(training)


@router.post("")
async def post_training(
    training: CreateTraining,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Create a new training"""
    async with session.begin():
        session.add(DBTraining(**training.dict()))
