from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Callable
from src.api.model.training import Training
from src.auth import User, get_user
from src.db.utils import get_session

from src.metrics.reports import get_reporter


SessionDep = Annotated[AsyncSession, Depends(get_session)]
ReporterDep = Annotated[Callable[[Training], None], Depends(get_reporter)]
UserDep = Annotated[User, Depends(get_user)]
