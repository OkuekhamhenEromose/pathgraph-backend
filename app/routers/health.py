"""
Health check endpoint.
Verifies CognoDB connectivity without exposing internal details.
"""

from fastapi import APIRouter, Request
import structlog

router = APIRouter(tags=["health"])
logger = structlog.get_logger()


@router.get("/health")
def health_check(request: Request):
    """
    Returns service health status.
    Attempts to verify database connectivity.
    """
    db_status = "connected"

    try:
        if hasattr(request.app.state, "db") and request.app.state.db is not None:
            request.app.state.db.verify_connectivity()
        else:
            db_status = "uninitialized"
            logger.warning("Database driver not initialized")
    except Exception as exc:
        db_status = "disconnected"
        logger.error("Database connectivity check failed", error=str(exc))

    status_code = 200 if db_status == "connected" else 503
    status = "healthy" if db_status == "connected" else "degraded"

    return {
        "status": status,
        "database": db_status,
        "service": "pathgraph-api"
    }
