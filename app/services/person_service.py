"""
Person service — thin business logic layer.
Transforms repository data for API responses.
"""

from app.repositories.graph_repository import GraphRepository
from app.core.exceptions import NotFoundError


class PersonService:
    def __init__(self, repo: GraphRepository) -> None:
        self.repo = repo

    def list_persons(self) -> list:
        return self.repo.get_all_persons()

    def get_person_detail(self, person_id: str) -> dict:
        person = self.repo.get_person_by_id(person_id)
        if not person:
            raise NotFoundError(f"Person '{person_id}' not found")
        return person

    def get_person_skills(self, person_id: str) -> list:
        # Confirm the person exists before returning their skills,
        # so an unknown person_id is a 404 rather than a silent empty list.
        if not self.repo.get_person_by_id(person_id):
            raise NotFoundError(f"Person '{person_id}' not found")
        return self.repo.get_person_skills(person_id)
