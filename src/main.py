from contextlib import asynccontextmanager
from typing import AsyncGenerator
from time import sleep
from logging import error, debug

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from alembic.config import Config
from alembic import command

from src.trainings import router


def upgrade_db() -> None:
    """upgrade DB via 'alembic upgrade head'"""
    while True:
        try:
            debug("upgrading database.")
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            break
        except Exception as e:
            error(f"failed to upgrade. {e}")
            sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    upgrade_db()
    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
