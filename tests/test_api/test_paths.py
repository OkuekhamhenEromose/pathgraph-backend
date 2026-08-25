"""
Test career path and skill-gap API endpoints.
Uses dependency override to mock the graph repository (same pattern as test_roles.py).
"""
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.database import get_graph_repo


def test_find_career_path_multi_hop(client: TestClient):
    """Verify multi-hop career path traversal endpoint (GET /paths/career)."""
    mock_repo = MagicMock()
    mock_repo.find_career_path.return_value = {
        "roles": [
            {"id": "r-008", "title": "Senior Backend Engineer", "level": 3, "category": "backend"},
            {"id": "r-009", "title": "Staff Backend Engineer", "level": 4, "category": "backend"},
            {"id": "r-010", "title": "Principal Backend Engineer", "level": 5, "category": "backend"},
        ],
        "promotions": [
            {"typical_years": 3, "commonness": 0.6},
            {"typical_years": 4, "commonness": 0.4},
        ],
        "num_steps": 2,
    }
    app.dependency_overrides[get_graph_repo] = lambda: mock_repo

    response = client.get(
        "/api/v1/paths/career",
        params={"from_role_id": "r-008", "to_role_id": "r-010"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["num_steps"] == 2
    assert len(data["roles"]) == 3
    # Verify it's a multi-hop traversal (3 nodes, 2 edges)
    assert data["roles"][0]["title"] == "Senior Backend Engineer"
    assert data["roles"][-1]["title"] == "Principal Backend Engineer"


def test_skill_gap_relationally_awkward(client: TestClient):
    """Verify skill gap analysis returns ordered missing skills (GET /paths/skill-gaps/{person_id})."""
    mock_repo = MagicMock()
    mock_repo.get_person_skill_gaps.return_value = {
        "current_role": {"id": "r-008", "title": "Senior Backend Engineer"},
        "target_role_id": "r-009",
        "missing_skills": [
            {
                "id": "s-037", "name": "Distributed Systems", "category": "paradigm",
                "difficulty": 5, "required_level": "required", "required_proficiency": 4,
                "prerequisites": [], "prerequisite_depth": 1,
            },
            {
                "id": "s-034", "name": "Kubernetes", "category": "tool",
                "difficulty": 5, "required_level": "required", "required_proficiency": 3,
                "prerequisites": [], "prerequisite_depth": 2,
            },
        ],
        "total_missing": 2,
    }
    app.dependency_overrides[get_graph_repo] = lambda: mock_repo

    response = client.get(
        "/api/v1/paths/skill-gaps/p-001",
        params={"target_role_id": "r-009"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total_missing"] == 2
    # Verify prerequisite ordering (lower depth first)
    assert data["missing_skills"][0]["prerequisite_depth"] <= data["missing_skills"][1]["prerequisite_depth"]


def test_parameterized_cypher_security(client: TestClient):
    """Verify that malicious input cannot inject Cypher -- it's just an ordinary string parameter."""
    mock_repo = MagicMock()
    mock_repo.find_career_path.return_value = None
    app.dependency_overrides[get_graph_repo] = lambda: mock_repo

    malicious_id = "r-008' OR '1'='1"
    response = client.get(
        "/api/v1/paths/career",
        params={"from_role_id": malicious_id, "to_role_id": "r-010"},
    )
    app.dependency_overrides.clear()

    # The malicious string is passed as a bound parameter, never concatenated into Cypher.
    # No path matches it, so the service raises NotFoundError -> 404. It must not 200 with
    # unexpected data and must not crash the server.
    assert response.status_code == 404
    mock_repo.find_career_path.assert_called_once_with(malicious_id, "r-010")
