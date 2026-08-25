"""
Test role API endpoints.
Uses dependency override to mock the graph repository.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.database import get_graph_repo


def mock_repo_with_roles():
    """Return a mocked repository with sample role data."""
    mock = MagicMock()
    mock.get_all_roles.return_value = [
        {
            "id": "r-sr-be",
            "title": "Senior Backend Engineer",
            "level": 3,
            "category": "backend",
            "track_name": "Individual Contributor"
        }
    ]
    mock.get_role_by_id.return_value = {
        "id": "r-sr-be",
        "title": "Senior Backend Engineer",
        "level": 3,
        "category": "backend",
        "track_name": "Individual Contributor"
    }
    mock.get_role_skills.return_value = [
        {
            "id": "s-python",
            "name": "Python",
            "category": "language",
            "requirement_level": "required",
            "required_proficiency": 4
        }
    ]
    return mock


def test_list_roles(client: TestClient):
    app.dependency_overrides[get_graph_repo] = mock_repo_with_roles
    response = client.get("/api/v1/roles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Senior Backend Engineer"
    app.dependency_overrides.clear()


def test_get_role_detail(client: TestClient):
    app.dependency_overrides[get_graph_repo] = mock_repo_with_roles
    response = client.get("/api/v1/roles/r-sr-be")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Senior Backend Engineer"
    assert len(data["required_skills"]) == 1
    app.dependency_overrides.clear()
