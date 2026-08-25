"""
Path service — career path and skill gap analysis.
"""

from app.repositories.graph_repository import GraphRepository
from app.core.exceptions import NotFoundError


class PathService:
    def __init__(self, repo: GraphRepository) -> None:
        self.repo = repo

    def find_career_path(self, from_role_id: str, to_role_id: str) -> dict:
        path = self.repo.find_career_path(from_role_id, to_role_id)
        if not path:
            raise NotFoundError(
                f"No career path found from '{from_role_id}' to '{to_role_id}'. "
                "Roles may be on different tracks or the target may not be reachable."
            )
        return path

    def analyze_skill_gaps(self, person_id: str, target_role_id: str) -> dict:
        if not self.repo.get_person_by_id(person_id):
            raise NotFoundError(f"Person '{person_id}' not found")
        if not self.repo.get_role_by_id(target_role_id):
            raise NotFoundError(f"Role '{target_role_id}' not found")
        return self.repo.get_person_skill_gaps(person_id, target_role_id)
