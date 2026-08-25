"""
FastAPI dependency injection for graph database access.
Provides a repository instance with a managed session per request.
"""

from fastapi import Request, HTTPException
from app.repositories.graph_repository import GraphRepository


def get_graph_repo(request: Request):
    """
    Dependency that yields a GraphRepository with a live session.
    Session is closed after the request, even if an exception occurs.
    """
    if not hasattr(request.app.state, "db") or request.app.state.db is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "DATABASE_UNAVAILABLE",
                "message": "Career data is temporarily unavailable. Please try again."
            }
        )

    session = None
    try:
        session = request.app.state.db.get_session()
        yield GraphRepository(session)
    except Exception as exc:
        # Log the real error, but return a safe message
        raise HTTPException(
            status_code=503,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to retrieve career data at this time."
            }
        ) from exc
    finally:
        if session is not None:
            session.close()
