from pydantic import BaseModel
from typing import List


class RecommendRequest(BaseModel):
    conditions: List[str]
    latitude: float
    longitude: float