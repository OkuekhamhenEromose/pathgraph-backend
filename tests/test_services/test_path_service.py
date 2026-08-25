"""
Test PathService business logic in isolation (no HTTP, no database).

PathService is constructed with a GraphRepository and delegates to it --
it never touches a raw neo4j session directly.
"""
import pytest
from unittest.mock import MagicMock
from app.services.path_service import PathService
from app.core.exceptions import NotFoundError


def test_find_career_path_not_found():
    """Verify NotFoundError when the repository finds no path."""
    mock_repo = MagicMock()
    mock_repo.find_career_path.return_value = None

    service = PathService(mock_repo)

    with pytest.raises(NotFoundError):
        service.find_career_path("r-001", "r-999")

    mock_repo.find_career_path.assert_called_once_with("r-001", "r-999")


def test_find_career_path_found():
    """Verify the service passes through a successful path result unchanged."""
    mock_repo = MagicMock()
    mock_repo.find_career_path.return_value = {
        "roles": [{"id": "r-001"}, {"id": "r-002"}],
        "promotions": [{"typical_years": 2}],
        "num_steps": 1,
    }

    service = PathService(mock_repo)
    result = service.find_career_path("r-001", "r-002")

    assert result["num_steps"] == 1
    assert len(result["roles"]) == 2
