"""Starlette application factory for Cal26."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .logging import configure_logging
from .middleware import RequestIdMiddleware

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"

load_dotenv()
configure_logging()
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


async def homepage(_: Request) -> Response:
    """Render a placeholder homepage."""
    return PlainTextResponse("Cal26 backend is running.")


async def health(_: Request) -> Response:
    """Simple readiness endpoint for monitoring."""
    return JSONResponse({"status": "ok"})


@asynccontextmanager
async def lifespan(_: Starlette) -> AsyncIterator[None]:
    """Manage application startup and shutdown logic."""
    logger.info("cal26 app starting")
    try:
        yield
    finally:
        logger.info("cal26 app shutting down")


def create_app() -> Starlette:
    """Create and configure the Starlette application."""
    app = Starlette(
        debug=os.getenv("APP_DEBUG", "false").lower() == "true",
        routes=[
            Route("/", homepage),
            Route("/health", health),
        ],
        lifespan=lifespan,
    )

    app.add_middleware(RequestIdMiddleware)

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    return app
