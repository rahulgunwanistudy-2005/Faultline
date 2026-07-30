from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .middleware import RequestSafetyMiddleware
from .routes.api import router

ROOT = Path(__file__).resolve().parents[3]
STATIC_ROOT = ROOT / "apps" / "web-static"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(
    title="Faultline API",
    version="0.2.0",
    description="Evidence-led inference of executable student procedures.",
    docs_url=None,
    redoc_url=None,
)
app.add_middleware(RequestSafetyMiddleware)
if get_settings().cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(get_settings().cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type", "X-Filename", "X-Request-ID"],
    )
app.include_router(router)
app.mount("/assets", StaticFiles(directory=STATIC_ROOT / "assets"), name="assets")


@app.get("/", include_in_schema=False)
def web_app() -> FileResponse:
    return FileResponse(STATIC_ROOT / "index.html")


@app.get("/judge", include_in_schema=False)
def judge_mode() -> FileResponse:
    return FileResponse(STATIC_ROOT / "judge.html")
