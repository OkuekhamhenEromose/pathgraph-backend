import pytest
from unittest.mock import MagicMock
from app.services.path_service import PathService
from app.core.exceptions import NotFoundError

def test_find_career_path_not_found(mock_session):
    """Verify NotFoundError when no path exists."""
    mock_result = MagicMock()
    mock_result.single.return_value = None
    mock_session.run.return_value = mock_result

    service = PathService(mock_session)
    with pytest.raises(NotFoundError):
        service.find_career_path("r-001", "r-999")
