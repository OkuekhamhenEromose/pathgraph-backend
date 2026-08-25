from pydantic import BaseModel
from typing import Optional, List


class SkillBase(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = None
    difficulty: Optional[int] = None


class SkillResponse(SkillBase):
    requirement_level: Optional[str] = None
    required_proficiency: Optional[int] = None


class SkillPrerequisitePath(BaseModel):
    path: List[dict]
    depth: int


class SkillDetailResponse(SkillBase):
    prerequisite_paths: List[SkillPrerequisitePath] = []
