from pydantic import BaseModel
from typing import List, Optional


class CareerTrackBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class CareerTrackResponse(CareerTrackBase):
    roles: Optional[List[dict]] = None
