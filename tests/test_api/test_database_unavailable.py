"""
Test graceful degradation when CognoDB is unreachable.

app.state.db is only None before the lifespan has set it up (or if the
driver failed to construct). get_graph_repo() checks for that and raises
a 503 before ever touching the database -- that's the behavior under test.
"""
from fastapi.testclient import TestClient
from app.main import app


def test_database_unavailable_returns_503(client: TestClient):
    original_db = getattr(app.state, "db", None)
    app.state.db = None
    try:
        response = client.get("/api/v1/roles")
        assert response.status_code == 503
        data = response.json()
        assert data["detail"]["code"] == "DATABASE_UNAVAILABLE"
        assert "temporarily unavailable" in data["detail"]["message"].lower()
    finally:
        app.state.db = original_db
