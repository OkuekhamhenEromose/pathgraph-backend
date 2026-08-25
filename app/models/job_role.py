from pydantic import BaseModel
from typing import Optional, List


class JobRoleBase(BaseModel):
    id: str
    title: str
    level: int
    category: str
    description: Optional[str] = None
    typical_years_experience: Optional[int] = None


class JobRoleResponse(JobRoleBase):
    track_name: Optional[str] = None
    required_skills: Optional[List[dict]] = None
