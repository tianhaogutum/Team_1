from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.v1 import sample
from .database import close_db, init_db
from .settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    init_db(settings)
    yield
    # Shutdown
    await close_db()


def create_app() -> FastAPI:
    """
    Application factory that configures FastAPI along with shared dependencies.
    """
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
    )

    @app.get("/healthz", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(sample.router, prefix="/api/v1")

    return app


app = create_app()

