"""
Career track API.
"""

from fastapi import APIRouter, Depends
from typing import List
from app.dependencies.database import get_graph_repo
from app.repositories.graph_repository import GraphRepository
from app.models.track import CareerTrackBase, CareerTrackResponse

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("", response_model=List[CareerTrackBase])
def list_tracks(repo: GraphRepository = Depends(get_graph_repo)):
    """List all career tracks."""
    return repo.get_all_tracks()


@router.get("/{track_id}", response_model=CareerTrackResponse)
def get_track(track_id: str, repo: GraphRepository = Depends(get_graph_repo)):
    """Get a career track with all roles in that track."""
    track = repo.get_track_with_roles(track_id)
    if not track:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(f"Track '{track_id}' not found")
    return track
