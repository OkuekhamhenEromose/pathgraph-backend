"""
Skill exploration API.
"""

from fastapi import APIRouter, Depends
from typing import List
from app.dependencies.database import get_graph_repo
from app.repositories.graph_repository import GraphRepository
from app.services.skill_service import SkillService
from app.models.skill import SkillBase, SkillDetailResponse

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=List[SkillBase])
def list_skills(repo: GraphRepository = Depends(get_graph_repo)):
    """List all skills."""
    service = SkillService(repo)
    return service.list_skills()


@router.get("/{skill_id}", response_model=SkillDetailResponse)
def get_skill(skill_id: str, repo: GraphRepository = Depends(get_graph_repo)):
    """Get a skill with its prerequisite chains (multi-hop traversal)."""
    service = SkillService(repo)
    return service.get_skill_detail(skill_id)
