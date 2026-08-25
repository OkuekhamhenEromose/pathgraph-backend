from pydantic import BaseModel
from typing import List, Optional


class CareerPathResponse(BaseModel):
    roles: List[dict]
    promotions: List[dict]
    num_steps: int


class SkillGapItem(BaseModel):
    id: str
    name: str
    category: str
    difficulty: Optional[int] = None
    required_level: str
    required_proficiency: Optional[int] = None
    prerequisites: List[dict] = []
    prerequisite_depth: int = 0


class SkillGapResponse(BaseModel):
    current_role: Optional[dict] = None
    target_role_id: str
    missing_skills: List[SkillGapItem]
    total_missing: int
