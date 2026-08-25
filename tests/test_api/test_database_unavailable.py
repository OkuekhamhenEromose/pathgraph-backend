from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_database_unavailable_returns_503():
    """Verify 503 when database connection is missing."""
    with patch("app.dependencies.database.get_db_connection") as mock_get_conn:
        mock_get_conn.side_effect = RuntimeError("Database connection has not been initialized")

        response = client.get("/api/v1/roles")
        assert response.status_code == 503
        data = response.json()
        assert "temporarily unavailable" in data["detail"].lower()
