"""
Person exploration API.
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.dependencies.database import get_graph_repo
from app.repositories.graph_repository import GraphRepository
from app.services.person_service import PersonService

router = APIRouter(prefix="/persons", tags=["persons"])


@router.get("", response_model=List[Dict[str, Any]])
def list_persons(repo: GraphRepository = Depends(get_graph_repo)):
    """List all people with their current role."""
    service = PersonService(repo)
    return service.list_persons()


@router.get("/{person_id}", response_model=Dict[str, Any])
def get_person(person_id: str, repo: GraphRepository = Depends(get_graph_repo)):
    """Get a single person with their current role."""
    service = PersonService(repo)
    return service.get_person_detail(person_id)


@router.get("/{person_id}/skills", response_model=List[Dict[str, Any]])
def get_person_skills(person_id: str, repo: GraphRepository = Depends(get_graph_repo)):
    """Get all skills held by a person."""
    service = PersonService(repo)
    return service.get_person_skills(person_id)
