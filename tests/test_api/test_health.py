"""
Test health check endpoint.
"""

from fastapi.testclient import TestClient


def test_health_check_returns_status(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert data["service"] == "pathgraph-api"


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "PathGraph"
