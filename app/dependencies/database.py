"""
FastAPI dependency injection for graph database access.
Provides a repository instance with a managed session per request.
"""

from fastapi import Request
from app.repositories.graph_repository import GraphRepository
from app.core.exceptions import DatabaseError


def get_graph_repo(request: Request):
    """
    Dependency that yields a GraphRepository with a live session.
    Session is closed after the request, even if an exception occurs.

    Raises DatabaseError (not HTTPException) on any failure so the
    response goes through main.py's database_error_handler and matches
    the same {"error": {"code", "message"}} envelope every other
    failure in the API returns.
    """
    if not hasattr(request.app.state, "db") or request.app.state.db is None:
        raise DatabaseError("Career data is temporarily unavailable. Please try again.")

    session = None
    try:
        session = request.app.state.db.get_session()
        yield GraphRepository(session)
    except DatabaseError:
        raise
    except Exception as exc:
        raise DatabaseError("Unable to retrieve career data at this time.") from exc
    finally:
        if session is not None:
            session.close()
