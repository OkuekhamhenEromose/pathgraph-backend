"""
FastAPI application factory.
Handles startup/shutdown lifespan, CORS, exception handlers, and router registration.
"""

from contextlib import asynccontextmanager
from sys import prefix
import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.exceptions import DatabaseError, NotFoundError
from app.database.connection import GraphDatabaseConnection
from app.routers import health, roles, skills, paths, tracks, persons

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Startup: create Neo4j driver and verify connectivity.
    Shutdown: close driver and drain connection pool.
    """
    # Startup
    setup_logging()
    logger.info("Starting PathGraph API", app_name=settings.app_name)

    app.state.db = GraphDatabaseConnection(
        uri=settings.cognodb_uri,
        username=settings.cognodb_username,
        password=settings.cognodb_password
    )

    try:
        app.state.db.verify_connectivity()
        logger.info("Connected to CognoDB")
    except Exception as exc:
        logger.error("Failed to connect to CognoDB", error=str(exc))
        # Do NOT raise — let the app start so health checks can report degraded status

    yield

    # Shutdown
    if hasattr(app.state, "db") and app.state.db is not None:
        app.state.db.close()
        logger.info("Disconnected from CognoDB")


app = FastAPI(
    title=settings.app_name,
    description="Career Path Navigator backed by CognoDB graph database",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — restrict to frontend origin only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# EXCEPTION HANDLERS
# ─────────────────────────────────────────────

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": str(exc)
            }
        }
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    logger.error("Database error", error=str(exc))
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Career data is temporarily unavailable. Please try again."
            }
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later."
            }
        }
    )


# ─────────────────────────────────────────────
# ROUTERS
# ─────────────────────────────────────────────

app.include_router(health.router)
app.include_router(roles.router, prefix="/api/v1")
app.include_router(skills.router, prefix="/api/v1")
app.include_router(paths.router, prefix="/api/v1")
app.include_router(tracks.router, prefix="/api/v1")
app.include_router(persons.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs"
    }
