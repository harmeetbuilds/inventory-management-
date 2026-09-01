from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Product

router = APIRouter()


@router.post("/recommend/{product_id}")
async def recommend_forecast(product_id: int, db: Session = Depends(get_db)):
    # 1. Fetch real product record from the DB
    product = (
        db.query(Product).filter(Product.id == product_id).first()
    )

    # Return 404 if product doesn't exist in database
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product with ID {product_id} not found"
        )

    # 2. Extract real stock from database
    current_stock = product.stock_quantity

    # 3. Predict demand (ML Model call or dynamic calculation)
    # e.g., predicted_demand = ml_model.predict(product_id)
    daily_forecasts = [8, 12, 10, 15, 9, 11, 7]
    predicted_demand = sum(daily_forecasts)

    # 4. Calculate recommended reorder quantity
    recommended_reorder = max(0, predicted_demand - current_stock)

    # 5. Evaluate alert severity based on live stock vs demand
    if current_stock < (predicted_demand * 0.5):
        alert_severity = "CRITICAL"
    elif current_stock < predicted_demand:
        alert_severity = "HIGH"
    else:
        alert_severity = "LOW"

    # 6. Return response to dashboard
    return {
        "product_id": product.id,
        "product_name": product.name,
        "current_stock": current_stock,
        "predicted_demand": predicted_demand,
        "recommended_reorder": recommended_reorder,
        "alert_severity": alert_severity,
        "daily_forecasts": daily_forecasts,
    }