
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents, health
from app.core.config import get_settings
from app.core.errors import register_exception_handlers


logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Backend for AI WorkHub: upload documents "
        "and ask questions about them."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(documents.router, prefix="/api")
