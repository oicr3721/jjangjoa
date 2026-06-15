from pydantic import BaseModel
from typing import List, Optional


class RecommendRequest(BaseModel):
    conditions: List[str] = []
    free_text: Optional[str] = ""   # 자유 입력 조건
    latitude: float
    longitude: float
