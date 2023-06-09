import re
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware import Middleware

from src.auth import ApikeyMiddleware
from src.logging import info
from src.db.migration import upgrade_db


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncGenerator[None, None]:
    info("Upgrading DB")

    await upgrade_db()

    yield


app = FastAPI(
    lifespan=lifespan,
    title="Kinetix",
    version="0.1.0",
    description="Kinetix's trainings service API",
    docs_url=None,
    middleware=[Middleware(ApikeyMiddleware)],
)


origins_regex = re.compile(
    (
        r"https?:\/\/"  # http:// or https://
        r"(localhost(:[0-9]*)?|"  # localhost, localhost:$PORT or ...
        r"[\w\.-]*(megaredhand|fedecolangelo)\.cloud\.okteto\.net)"  # okteto
    )
)

# ----------
# Subrouting
# ----------


def add_subrouters(app: FastAPI) -> None:
    """Set up subrouters"""
    from src.api.trainings import router as trainings_router
    from src.api.favorites import router as favorites_router

    app.include_router(trainings_router)
    app.include_router(favorites_router)


add_subrouters(app)


# -----------------
# Utility endpoints
# -----------------


@app.get("/health", include_in_schema=False)
def health_check() -> Dict[str, str]:
    """Check if server is responsive"""
    return {"status": "Alive and kicking!"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse("favicon.ico")


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title,
        swagger_favicon_url="favicon.ico",
    )
