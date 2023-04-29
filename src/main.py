from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.trainings import router
from src.logging import info
from src.db.migration import upgrade_db


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncGenerator[None, None]:
    info("Upgrading DB")

    await upgrade_db()

    yield


app = FastAPI(lifespan=lifespan, title="Kinetix", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/health", include_in_schema=False)
def health_check() -> Dict[str, str]:
    """Check if server is responsive"""
    return {"status": "Alive and kicking!"}
