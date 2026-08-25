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

def test_analyze_skill_gaps_unknown_person_raises_not_found():
    """A bogus person_id must 404, not silently return a full gap list."""
    mock_repo = MagicMock()
    mock_repo.get_person_by_id.return_value = None

    service = PathService(mock_repo)

    with pytest.raises(NotFoundError):
        service.analyze_skill_gaps("p-999", "r-sr-be")

    mock_repo.get_person_skill_gaps.assert_not_called()


def test_analyze_skill_gaps_unknown_role_raises_not_found():
    """A bogus target_role_id must 404 too."""
    mock_repo = MagicMock()
    mock_repo.get_person_by_id.return_value = {"id": "p-001", "name": "Alex Chen"}
    mock_repo.get_role_by_id.return_value = None

    service = PathService(mock_repo)

    with pytest.raises(NotFoundError):
        service.analyze_skill_gaps("p-001", "r-999")

    mock_repo.get_person_skill_gaps.assert_not_called()


def test_analyze_skill_gaps_passes_through_when_valid():
    """Valid person + role: delegates to the repository unchanged."""
    mock_repo = MagicMock()
    mock_repo.get_person_by_id.return_value = {"id": "p-001", "name": "Alex Chen"}
    mock_repo.get_role_by_id.return_value = {"id": "r-sr-be", "title": "Senior Backend Engineer"}
    mock_repo.get_person_skill_gaps.return_value = {
        "current_role": {"id": "r-be"},
        "target_role_id": "r-sr-be",
        "missing_skills": [],
        "total_missing": 0,
    }

    service = PathService(mock_repo)
    result = service.analyze_skill_gaps("p-001", "r-sr-be")

    assert result["total_missing"] == 0
    mock_repo.get_person_skill_gaps.assert_called_once_with("p-001", "r-sr-be")
