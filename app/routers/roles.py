"""
Role exploration API.
"""

from fastapi import APIRouter, Depends
from typing import List
from app.dependencies.database import get_graph_repo
from app.repositories.graph_repository import GraphRepository
from app.services.role_service import RoleService
from app.models.job_role import JobRoleBase, JobRoleResponse

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=List[JobRoleBase])
def list_roles(repo: GraphRepository = Depends(get_graph_repo)):
    """List all job roles."""
    service = RoleService(repo)
    return service.list_roles()


@router.get("/{role_id}", response_model=JobRoleResponse)
def get_role(role_id: str, repo: GraphRepository = Depends(get_graph_repo)):
    """Get a job role with its required skills."""
    service = RoleService(repo)
    return service.get_role_detail(role_id)
