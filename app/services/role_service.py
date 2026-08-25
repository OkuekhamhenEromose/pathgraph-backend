"""
Role service — thin business logic layer.
Transforms repository data for API responses.
"""

from app.repositories.graph_repository import GraphRepository
from app.core.exceptions import NotFoundError


class RoleService:
    def __init__(self, repo: GraphRepository) -> None:
        self.repo = repo

    def list_roles(self) -> list:
        return self.repo.get_all_roles()

    def get_role_detail(self, role_id: str) -> dict:
        role = self.repo.get_role_by_id(role_id)
        if not role:
            raise NotFoundError(f"Role '{role_id}' not found")
        role["required_skills"] = self.repo.get_role_skills(role_id)
        return role
