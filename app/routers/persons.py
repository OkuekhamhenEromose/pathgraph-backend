from fastapi import APIRouter, Depends
from neo4j import Session
from app.dependencies.database import get_db_session
from app.repositories.graph_repository import GraphRepository
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/api/v1/persons", tags=["persons"])

@router.get("")
def list_persons(session: Session = Depends(get_db_session)):
    repo = GraphRepository(session)
    return repo.get_all_persons()

@router.get("/{person_id}")
def get_person(person_id: str, session: Session = Depends(get_db_session)):
    repo = GraphRepository(session)
    person = repo.get_person_by_id(person_id)
    if not person:
        raise NotFoundError(f"Person '{person_id}' not found")
    return person

@router.get("/{person_id}/skills")
def get_person_skills(person_id: str, session: Session = Depends(get_db_session)):
    repo = GraphRepository(session)
    return repo.get_person_skills(person_id)
