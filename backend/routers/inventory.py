from fastapi import APIRouter, Depends, HTTPException
from backend.core.database import get_db
from backend.schemas.inventory import RecommendationResponse
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory Management"])

@router.get("/alerts")
def get_active_alerts(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, p.name as product_name 
        FROM inventory_alerts a
        JOIN products p ON a.product_id = p.product_id
        WHERE a.is_resolved = 0
        ORDER BY a.created_at DESC;
    """)
    alerts = cursor.fetchall()
    cursor.close()
    return {"alerts": alerts}

@router.patch("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("UPDATE inventory_alerts SET is_resolved = 1 WHERE alert_id = %s;", (alert_id,))
    db.commit()
    cursor.close()
    return {"status": "success", "message": f"Alert {alert_id} resolved."}