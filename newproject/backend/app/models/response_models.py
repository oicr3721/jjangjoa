from pydantic import BaseModel
from typing import List


class RestaurantResponse(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    distance_km: float
    score: float
    matched_keywords: List[str]


class RecommendResponse(BaseModel):
    restaurants: List[RestaurantResponse]