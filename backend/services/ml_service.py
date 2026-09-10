import joblib
import pandas as pd
from datetime import timedelta
from fastapi import HTTPException
from backend.core.config import settings

class MLService:
    def __init__(self):
        try:
            self.model = joblib.load(settings.MODEL_PATH)
        except Exception as e:
            self.model = None
            print(f"Warning: Model not loaded from {settings.MODEL_PATH}: {e}")

    def generate_recommendation_and_forecast(self, db_conn, product_id: int):
        if not self.model:
            raise HTTPException(status_code=500, detail="ML model file is not available.")

        cursor = db_conn.cursor(dictionary=True)

        # Fetch product metadata
        cursor.execute("""
            SELECT product_id, name, current_stock, reorder_level, safety_stock
            FROM products WHERE product_id = %s;
        """, (product_id,))
        product_info = cursor.fetchone()

        if not product_info:
            cursor.close()
            raise HTTPException(status_code=404, detail="Product not found")

        # Fetch daily product sales history
        cursor.execute("""
            SELECT sale_date, quantity_sold
            FROM daily_product_sales
            WHERE product_id = %s
            ORDER BY sale_date;
        """, (product_id,))
        sales_records = cursor.fetchall()

        if len(sales_records) < 14:
            cursor.close()
            raise HTTPException(status_code=400, detail="Insufficient sales history for forecasting (minimum 14 days required).")

        df = pd.DataFrame(sales_records)
        df["sale_date"] = pd.to_datetime(df["sale_date"])

        history = df["quantity_sold"].tolist()
        last_date = df["sale_date"].max()

        features = [
            "product_id", "day_of_week", "day_of_month",
            "month", "week_of_year", "lag_1", "lag_7",
            "lag_14", "rolling_7", "rolling_14"
        ]

        predictions = []

        # Predict next 7 days recursively
        for i in range(1, 8):
            future_date = last_date + timedelta(days=i)

            input_data = pd.DataFrame([{
                "product_id": product_id,
                "day_of_week": future_date.dayofweek,
                "day_of_month": future_date.day,
                "month": future_date.month,
                "week_of_year": int(future_date.isocalendar().week),
                "lag_1": history[-1],
                "lag_7": history[-7],
                "lag_14": history[-14],
                "rolling_7": sum(history[-7:]) / 7,
                "rolling_14": sum(history[-14:]) / 14
            }])

            pred = self.model.predict(input_data[features])[0]
            pred = max(0.0, float(pred))

            predictions.append((future_date.date(), pred))
            history.append(pred)

        # Inventory logic
        total_demand = sum(p for _, p in predictions)
        current_stock = int(product_info["current_stock"])
        reorder_level = int(product_info["reorder_level"])
        safety_stock = int(product_info["safety_stock"])

        required_stock = total_demand + safety_stock
        reorder_quantity = max(0, round(required_stock - current_stock))

        # Risk categorization
        if current_stock <= reorder_level:
            alert_type, severity = "STOCK_OUT_RISK", "HIGH"
            message = (f"Current stock ({current_stock}) is at or below reorder level ({reorder_level}). "
                       f"Predicted 7-day demand is {total_demand:.2f} units.")
        elif current_stock < total_demand:
            alert_type, severity = "STOCK_OUT_RISK", "MEDIUM"
            message = (f"Current stock ({current_stock}) may not cover predicted 7-day demand of "
                       f"{total_demand:.2f} units.")
        else:
            alert_type, severity = "LOW_STOCK", "LOW"
            message = f"Current stock ({current_stock}) is sufficient for predicted demand."

        # Database updates
        start_date, end_date = predictions[0][0], predictions[-1][0]

        cursor.execute("""
            DELETE FROM demand_forecasts
            WHERE product_id = %s AND forecast_date BETWEEN %s AND %s;
        """, (product_id, start_date, end_date))

        for forecast_date, pred in predictions:
            cursor.execute("""
                INSERT INTO demand_forecasts (product_id, forecast_date, predicted_quantity, model_name, model_version)
                VALUES (%s, %s, %s, %s, %s);
            """, (product_id, forecast_date, round(pred, 2), "Random Forest", "1.0"))

        cursor.execute("""
            INSERT INTO inventory_alerts (product_id, alert_type, severity, message, recommended_quantity, is_resolved)
            VALUES (%s, %s, %s, %s, %s, 0);
        """, (product_id, alert_type, severity, message, reorder_quantity))

        db_conn.commit()
        cursor.close()

        return RecommendationResponse(
            product_id=product_id,
            product_name=product_info["name"],
            current_stock=current_stock,
            reorder_level=reorder_level,
            safety_stock=safety_stock,
            predicted_7d_demand=round(total_demand, 2),
            required_stock=round(required_stock, 2),
            recommended_reorder_qty=reorder_quantity,
            alert_type=alert_type,
            severity=severity,
            message=message,
            daily_forecasts=[{"forecast_date": d, "predicted_quantity": round(q, 2)} for d, q in predictions]
        )

ml_service = MLService()