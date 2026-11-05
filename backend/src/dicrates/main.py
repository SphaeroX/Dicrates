"""FastAPI application factory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from dicrates import __version__
from dicrates.core.auth import verifier_for
from dicrates.core.db import create_pool
from dicrates.core.settings import Settings, get_settings
from dicrates.profiles.routes import router as profiles_router


class HealthResponse(BaseModel):
    status: str
    version: str


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        app.state.db_pool = None
        if settings.database_url is None:
            # /health works without a database; DB endpoints answer 503.
            yield
            return
        async with create_pool(settings.database_url.get_secret_value()) as pool:
            app.state.db_pool = pool
            yield

    app = FastAPI(title="Dicrates API", version=__version__, lifespan=lifespan)
    # Without SUPABASE_URL, authenticated endpoints answer 503.
    app.state.token_verifier = verifier_for(settings) if settings.supabase_url else None

    @app.get("/health")
    def health() -> HealthResponse:  # pyright: ignore[reportUnusedFunction]
        return HealthResponse(status="ok", version=__version__)

    app.include_router(profiles_router)
    return app


app = create_app()
