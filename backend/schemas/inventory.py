from pydantic import BaseModel
from datetime import date
from typing import List

class DailyForecast(BaseModel):
    forecast_date: date
    predicted_quantity: float

class RecommendationResponse(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    reorder_level: int
    safety_stock: int
    predicted_7d_demand: float
    required_stock: float
    recommended_reorder_qty: int
    alert_type: str
    severity: str
    message: str
    daily_forecasts: List[DailyForecast]