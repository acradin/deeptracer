"""ASGI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from deeptracer import __version__
from deeptracer.web.config import STATIC_DIR
from deeptracer.web.routes import router


def create_app() -> FastAPI:
    """
    Build the session-picker ASGI app.

    Args:
        None

    Returns:
        FastAPI app bound for use with uvicorn.

    Raises:
        None
    """
    app = FastAPI(title="DeepTracer", version=__version__)
    app.include_router(router)

    # Mount last so /static does not swallow API routes.
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app
