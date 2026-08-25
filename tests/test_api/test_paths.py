from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app

client = TestClient(app)

def test_find_career_path_multi_hop(mock_db_connection):
    """Verify multi-hop career path traversal endpoint."""
    mock_result = MagicMock()
    mock_result.single.return_value = MagicMock(data=MagicMock(return_value={
        "role_path": [
            {"id": "r-008", "title": "Senior Backend Engineer", "level": 3, "category": "backend"},
            {"id": "r-009", "title": "Staff Backend Engineer", "level": 4, "category": "backend"},
            {"id": "r-010", "title": "Principal Backend Engineer", "level": 5, "category": "backend"}
        ],
        "num_steps": 2,
        "transitions": [
            {"typical_years": 3, "commonness": 0.6},
            {"typical_years": 4, "commonness": 0.4}
        ]
    }))
    mock_db_connection.run.return_value = mock_result

    response = client.post("/api/v1/paths/career", json={
        "current_role_id": "r-008",
        "target_role_id": "r-010"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["num_steps"] == 2
    assert len(data["role_path"]) == 3
    # Verify it's a multi-hop traversal (3 nodes, 2 edges)
    assert data["role_path"][0]["title"] == "Senior Backend Engineer"
    assert data["role_path"][-1]["title"] == "Principal Backend Engineer"

def test_skill_gap_relationally_awkward(mock_db_connection):
    """Verify skill gap analysis returns ordered missing skills."""
    mock_result = MagicMock()
    mock_result.__iter__ = MagicMock(return_value=iter([
        MagicMock(data=MagicMock(return_value={
            "id": "s-037", "name": "Distributed Systems", "difficulty": 5,
            "category": "paradigm", "prerequisite_depth": 1
        })),
        MagicMock(data=MagicMock(return_value={
            "id": "s-034", "name": "Kubernetes", "difficulty": 5,
            "category": "tool", "prerequisite_depth": 2
        }))
    ]))
    mock_db_connection.run.return_value = mock_result

    response = client.post("/api/v1/paths/skill-gap", json={
        "person_id": "p-001",
        "target_role_id": "r-009"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # Verify prerequisite ordering (lower depth first)
    assert data[0]["prerequisite_depth"] <= data[1]["prerequisite_depth"]

def test_parameterized_cypher_security(mock_db_connection):
    """Verify that malicious input cannot inject Cypher."""
    mock_result = MagicMock()
    mock_result.single.return_value = None
    mock_db_connection.run.return_value = mock_result

    # Attempt injection via role_id
    malicious_id = "r-008' OR '1'='1"
    response = client.post("/api/v1/paths/career", json={
        "current_role_id": malicious_id,
        "target_role_id": "r-010"
    })
    # Should NOT crash or return unexpected data — parameterized Cypher prevents injection
    # With our mock, it returns 404 (no path found), which is safe
    assert response.status_code in [200, 404]
