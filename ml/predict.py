import joblib
import pandas as pd
from datetime import timedelta

from database import get_connection


# ==========================================
# 1. LOAD TRAINED MODEL
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
# 2. LOAD SALES DATA FROM MYSQL
# ==========================================

connection = get_connection()

query = """
SELECT
    product_id,
    sale_date,
    quantity_sold
FROM daily_product_sales
ORDER BY product_id, sale_date;
"""

df = pd.read_sql(query, connection)

connection.close()

df["sale_date"] = pd.to_datetime(df["sale_date"])


# ==========================================
# 3. ASK FOR PRODUCT ID
# ==========================================

product_id = int(input("Enter Product ID: "))


product_data = df[
    df["product_id"] == product_id
].copy()

product_data = product_data.sort_values("sale_date")


# ==========================================
# 4. CHECK DATA
# ==========================================

if len(product_data) < 14:
    print("Not enough sales history for this product.")
    exit()


# ==========================================
# 5. PREPARE HISTORY
# ==========================================

history = product_data["quantity_sold"].tolist()

last_date = product_data["sale_date"].max()


# ==========================================
# 6. PREDICT NEXT 7 DAYS
# ==========================================

future_predictions = []

for i in range(1, 8):

    future_date = last_date + timedelta(days=i)

    lag_1 = history[-1]
    lag_7 = history[-7]
    lag_14 = history[-14]

    rolling_7 = sum(history[-7:]) / 7
    rolling_14 = sum(history[-14:]) / 14

    input_data = pd.DataFrame([{
        "product_id": product_id,
        "day_of_week": future_date.dayofweek,
        "day_of_month": future_date.day,
        "month": future_date.month,
        "week_of_year": int(future_date.isocalendar().week),
        "lag_1": lag_1,
        "lag_7": lag_7,
        "lag_14": lag_14,
        "rolling_7": rolling_7,
        "rolling_14": rolling_14
    }])

    prediction = model.predict(
        input_data[features]
    )[0]

    prediction = max(0, prediction)

    future_predictions.append(
        (future_date.date(), prediction)
    )

    # Use this prediction as history
    # for the next day's prediction
    history.append(prediction)


# ==========================================
# 7. DISPLAY FORECAST
# ==========================================

print()
print("==============================")
print("7-DAY DEMAND FORECAST")
print("==============================")

total_demand = 0

for forecast_date, prediction in future_predictions:

    print(
        forecast_date,
        "→",
        round(prediction, 2),
        "units"
    )

    total_demand += prediction


print("------------------------------")

print(
    "Total predicted demand:",
    round(total_demand, 2),
    "units"
)