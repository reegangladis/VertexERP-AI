from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.exception_handler import setup_exception_handlers

# Initialize logging configuration
setup_logging()

# Create the FastAPI instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise AI Operating System - Project Foundation API",
    version="1.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register exception handlers
setup_exception_handlers(app)

# Include core API routes under version prefix
app.include_router(api_router, prefix=settings.API_V1_STR)
