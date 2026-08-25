"""
Skill service — business logic for skill exploration.
"""

from app.repositories.graph_repository import GraphRepository
from app.core.exceptions import NotFoundError


class SkillService:
    def __init__(self, repo: GraphRepository) -> None:
        self.repo = repo

    def list_skills(self) -> list:
        return self.repo.get_all_skills()

    def get_skill_detail(self, skill_id: str) -> dict:
        skill = self.repo.get_skill_by_id(skill_id)
        if not skill:
            raise NotFoundError(f"Skill '{skill_id}' not found")
        skill["prerequisite_paths"] = self.repo.get_skill_prerequisites(skill_id)
        return skill
