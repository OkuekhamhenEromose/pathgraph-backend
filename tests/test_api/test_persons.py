"""
Test person API endpoints.
Uses dependency override to mock the graph repository.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.database import get_graph_repo


def mock_repo_with_persons():
    """Return a mocked repository with sample person data."""
    mock = MagicMock()
    mock.get_all_persons.return_value = [
        {"id": "p-001", "name": "Alex Chen", "current_role": {"id": "r-sr-be", "title": "Senior Backend Engineer"}}
    ]
    mock.get_person_by_id.return_value = {
        "id": "p-001", "name": "Alex Chen", "current_role": {"id": "r-sr-be", "title": "Senior Backend Engineer"}
    }
    mock.get_person_skills.return_value = [
        {"id": "s-python", "name": "Python", "proficiency_level": 4}
    ]
    return mock


def test_list_persons(client: TestClient):
    app.dependency_overrides[get_graph_repo] = mock_repo_with_persons
    response = client.get("/api/v1/persons")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Alex Chen"
    app.dependency_overrides.clear()


def test_get_person_detail(client: TestClient):
    app.dependency_overrides[get_graph_repo] = mock_repo_with_persons
    response = client.get("/api/v1/persons/p-001")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alex Chen"
    app.dependency_overrides.clear()


def test_get_person_not_found(client: TestClient):
    mock = mock_repo_with_persons()
    mock.get_person_by_id.return_value = None
    app.dependency_overrides[get_graph_repo] = lambda: mock
    response = client.get("/api/v1/persons/p-999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"
    app.dependency_overrides.clear()


def test_get_person_skills(client: TestClient):
    app.dependency_overrides[get_graph_repo] = mock_repo_with_persons
    response = client.get("/api/v1/persons/p-001/skills")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["name"] == "Python"
    app.dependency_overrides.clear()


def test_get_person_skills_unknown_person_returns_404(client: TestClient):
    mock = mock_repo_with_persons()
    mock.get_person_by_id.return_value = None
    app.dependency_overrides[get_graph_repo] = lambda: mock
    response = client.get("/api/v1/persons/p-999/skills")
    assert response.status_code == 404
    mock.get_person_skills.assert_not_called()
    app.dependency_overrides.clear()
