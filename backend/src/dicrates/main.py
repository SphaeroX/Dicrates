"""FastAPI application factory."""

from fastapi import FastAPI
from pydantic import BaseModel

from dicrates import __version__


class HealthResponse(BaseModel):
    status: str
    version: str


def create_app() -> FastAPI:
    app = FastAPI(title="Dicrates API", version=__version__)

    @app.get("/health")
    def health() -> HealthResponse:  # pyright: ignore[reportUnusedFunction]
        return HealthResponse(status="ok", version=__version__)

    return app


app = create_app()
