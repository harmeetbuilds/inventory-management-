import joblib
import pandas as pd
from datetime import timedelta

from database import get_connection


# ==========================================
# 1. LOAD MODEL
# ==========================================

model = joblib.load("ml/model/demand_model.pkl")

features = [
    "product_id",
    "day_of_week",
    "day_of_month",
    "month",
    "week_of_year",
    "lag_1",
    "lag_7",
    "lag_14",
    "rolling_7",
    "rolling_14"
]


# ==========================================
# 2. ASK FOR PRODUCT
# ==========================================

product_id = int(input("Enter Product ID: "))


# ==========================================
# 3. CONNECT TO MYSQL
# ==========================================

connection = get_connection()


# ==========================================
# 4. GET PRODUCT INFORMATION
# ==========================================

product_query = """
SELECT
    product_id,
    name,
    current_stock,
    reorder_level,
    safety_stock
FROM products
WHERE product_id = %s;
"""

product = pd.read_sql(
    product_query,
    connection,
    params=[product_id]
)

if product.empty:
    print("Product not found.")
    connection.close()
    exit()


product_info = product.iloc[0]


# ==========================================
# 5. GET SALES HISTORY
# ==========================================

sales_query = """
SELECT
    product_id,
    sale_date,
    quantity_sold
FROM daily_product_sales
WHERE product_id = %s
ORDER BY sale_date;
"""

sales = pd.read_sql(
    sales_query,
    connection,
    params=[product_id]
)

sales["sale_date"] = pd.to_datetime(
    sales["sale_date"]
)

if len(sales) < 14:
    print("Not enough sales history.")
    connection.close()
    exit()


# ==========================================
# 6. PREPARE HISTORY
# ==========================================

history = sales["quantity_sold"].tolist()

last_date = sales["sale_date"].max()

predictions = []


# ==========================================
# 7. PREDICT NEXT 7 DAYS
# ==========================================

for i in range(1, 8):

    future_date = last_date + timedelta(days=i)

    input_data = pd.DataFrame([{
        "product_id": product_id,
        "day_of_week": future_date.dayofweek,
        "day_of_month": future_date.day,
        "month": future_date.month,
        "week_of_year": int(
            future_date.isocalendar().week
        ),
        "lag_1": history[-1],
        "lag_7": history[-7],
        "lag_14": history[-14],
        "rolling_7": sum(history[-7:]) / 7,
        "rolling_14": sum(history[-14:]) / 14
    }])

    prediction = model.predict(
        input_data[features]
    )[0]

    prediction = max(0, prediction)

    predictions.append(
        (future_date.date(), prediction)
    )

    history.append(prediction)


# ==========================================
# 8. CALCULATE INVENTORY
# ==========================================

total_demand = sum(
    prediction for _, prediction in predictions
)

current_stock = int(
    product_info["current_stock"]
)

reorder_level = int(
    product_info["reorder_level"]
)

safety_stock = int(
    product_info["safety_stock"]
)

required_stock = total_demand + safety_stock

reorder_quantity = max(
    0,
    round(required_stock - current_stock)
)


# ==========================================
# 9. DETERMINE RISK
# ==========================================

if current_stock <= reorder_level:

    alert_type = "STOCK_OUT_RISK"
    severity = "HIGH"

    message = (
        f"Current stock ({current_stock}) is at or "
        f"below the reorder level ({reorder_level}). "
        f"Predicted 7-day demand is "
        f"{total_demand:.2f} units."
    )

elif current_stock < total_demand:

    alert_type = "STOCK_OUT_RISK"
    severity = "MEDIUM"

    message = (
        f"Current stock ({current_stock}) may not "
        f"cover the predicted 7-day demand of "
        f"{total_demand:.2f} units."
    )

else:

    alert_type = "LOW_STOCK"
    severity = "LOW"

    message = (
        f"Current stock ({current_stock}) is "
        f"sufficient for the predicted demand."
    )


# ==========================================
# 10. SAVE 7-DAY FORECAST TO MYSQL
# ==========================================

# Remove old forecasts for these same dates
# so running the program again doesn't create
# duplicate forecasts.

start_date = predictions[0][0]
end_date = predictions[-1][0]

delete_forecasts = """
DELETE FROM demand_forecasts
WHERE product_id = %s
AND forecast_date BETWEEN %s AND %s;
"""

cursor = connection.cursor()

cursor.execute(
    delete_forecasts,
    (product_id, start_date, end_date)
)


insert_forecast = """
INSERT INTO demand_forecasts
(
    product_id,
    forecast_date,
    predicted_quantity,
    model_name,
    model_version
)
VALUES (%s, %s, %s, %s, %s);
"""


for forecast_date, prediction in predictions:

    cursor.execute(
        insert_forecast,
        (
            product_id,
            forecast_date,
            round(prediction, 2),
            "Random Forest",
            "1.0"
        )
    )


# ==========================================
# 11. SAVE INVENTORY ALERT
# ==========================================

insert_alert = """
INSERT INTO inventory_alerts
(
    product_id,
    alert_type,
    severity,
    message,
    recommended_quantity,
    is_resolved
)
VALUES (%s, %s, %s, %s, %s, 0);
"""

cursor.execute(
    insert_alert,
    (
        product_id,
        alert_type,
        severity,
        message,
        reorder_quantity
    )
)


# ==========================================
# 12. COMMIT EVERYTHING
# ==========================================

connection.commit()

cursor.close()
connection.close()


# ==========================================
# 13. DISPLAY RESULTS
# ==========================================

print()
print("====================================")
print("INVENTORY RECOMMENDATION")
print("====================================")

print("Product:", product_info["name"])
print("Product ID:", product_id)

print()
print("Current stock:", current_stock)
print("Reorder level:", reorder_level)
print("Safety stock:", safety_stock)

print()
print(
    "7-day predicted demand:",
    round(total_demand, 2),
    "units"
)

print(
    "Required stock:",
    round(required_stock, 2),
    "units"
)

print(
    "Recommended reorder:",
    reorder_quantity,
    "units"
)

print()
print("Status:", severity, "-", alert_type)

print()
print("7-day forecast saved to MySQL.")
print("Inventory alert saved to MySQL.")

print("====================================")