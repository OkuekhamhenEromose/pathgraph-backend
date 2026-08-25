"""
Career path and skill gap API.
Demonstrates multi-hop traversal and relationally awkward queries.
"""

from fastapi import APIRouter, Depends, Query
from app.dependencies.database import get_graph_repo
from app.repositories.graph_repository import GraphRepository
from app.services.path_service import PathService
from app.models.path import CareerPathResponse, SkillGapResponse

router = APIRouter(prefix="/paths", tags=["paths"])


@router.get("/career", response_model=CareerPathResponse)
def get_career_path(
    from_role_id: str = Query(..., description="Current role ID (e.g., r-sr-be)"),
    to_role_id: str = Query(..., description="Target role ID (e.g., r-staff-be)"),
    repo: GraphRepository = Depends(get_graph_repo)
):
    """
    Find the shortest career path between two roles.
    Uses native graph shortestPath algorithm (multi-hop traversal).
    """
    service = PathService(repo)
    return service.find_career_path(from_role_id, to_role_id)


@router.get("/skill-gaps/{person_id}", response_model=SkillGapResponse)
def get_skill_gaps(
    person_id: str,
    target_role_id: str = Query(..., description="Target role ID to analyze against"),
    repo: GraphRepository = Depends(get_graph_repo)
):
    """
    Analyze skill gaps for a person against a target role.
    Includes missing prerequisites (relationally awkward query).
    """
    service = PathService(repo)
    return service.analyze_skill_gaps(person_id, target_role_id)
