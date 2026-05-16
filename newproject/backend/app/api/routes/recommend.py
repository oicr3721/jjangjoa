from fastapi import APIRouter

from app.models.request_models import (
    RecommendRequest
)

from app.services.recommendation.recommendation_service import (
    RecommendationService
)

router = APIRouter()

service = RecommendationService()


@router.post("/recommend")
def recommend(request: RecommendRequest):

    restaurants = service.recommend(
        request.conditions,
        request.latitude,
        request.longitude
    )

    return {
        "restaurants": restaurants
    }