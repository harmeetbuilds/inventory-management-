from fastapi import APIRouter, Depends
from backend.core.database import get_db
from backend.schemas.inventory import RecommendationResponse
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/api/v1/forecast", tags=["ML Forecast & Inventory"])

@router.post("/recommend/{product_id}", response_model=RecommendationResponse)
def get_inventory_recommendation(product_id: int, db=Depends(get_db)):
    """
    Generates a 7-day demand forecast for a product, saves results to MySQL,
    creates inventory alerts, and returns actionable recommendations.
    """
    return ml_service.generate_recommendation_and_forecast(db, product_id)