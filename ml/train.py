import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

from database import get_connection


# ==========================================
# 1. LOAD DATA FROM MYSQL
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

print("Data loaded successfully!")
print("Rows:", len(df))


# ==========================================
# 2. PREPARE DATA
# ==========================================

df["sale_date"] = pd.to_datetime(df["sale_date"])

df = df.sort_values(
    ["product_id", "sale_date"]
).reset_index(drop=True)


# ==========================================
# 3. CREATE TIME FEATURES
# ==========================================

df["day_of_week"] = df["sale_date"].dt.dayofweek
df["day_of_month"] = df["sale_date"].dt.day
df["month"] = df["sale_date"].dt.month
df["week_of_year"] = df["sale_date"].dt.isocalendar().week.astype(int)


# ==========================================
# 4. CREATE LAG FEATURES
# ==========================================

df["lag_1"] = (
    df.groupby("product_id")["quantity_sold"]
    .shift(1)
)

df["lag_7"] = (
    df.groupby("product_id")["quantity_sold"]
    .shift(7)
)

df["lag_14"] = (
    df.groupby("product_id")["quantity_sold"]
    .shift(14)
)


# ==========================================
# 5. CREATE ROLLING FEATURES
# ==========================================

df["rolling_7"] = (
    df.groupby("product_id")["quantity_sold"]
    .transform(
        lambda x: x.shift(1).rolling(7).mean()
    )
)

df["rolling_14"] = (
    df.groupby("product_id")["quantity_sold"]
    .transform(
        lambda x: x.shift(1).rolling(14).mean()
    )
)


# Remove rows where features aren't available
df = df.dropna().reset_index(drop=True)


# ==========================================
# 6. DEFINE FEATURES AND TARGET
# ==========================================

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

X = df[features]

y = df["quantity_sold"]

# ==========================================
# 7. TIME-BASED TRAIN / TEST SPLIT
# ==========================================

train_parts = []
test_parts = []

for product_id, product_df in df.groupby("product_id"):

    product_df = product_df.sort_values("sale_date")

    split_index = int(len(product_df) * 0.8)

    train_parts.append(product_df.iloc[:split_index])
    test_parts.append(product_df.iloc[split_index:])


train_df = pd.concat(train_parts)
test_df = pd.concat(test_parts)


X_train = train_df[features]
y_train = train_df["quantity_sold"]

X_test = test_df[features]
y_test = test_df["quantity_sold"]


print()
print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))



print()
print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))


# ==========================================
# 8. TRAIN RANDOM FOREST
# ==========================================

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)


# ==========================================
# 9. MAKE PREDICTIONS
# ==========================================

predictions = model.predict(X_test)

# Demand cannot be negative
predictions = np.maximum(predictions, 0)


# ==========================================
# 10. EVALUATE MODEL
# ==========================================

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)


print()
print("==============================")
print("MODEL PERFORMANCE")
print("==============================")

print("MAE :", round(mae, 2))
print("RMSE:", round(rmse, 2))


# ==========================================
# 11. SHOW SOME PREDICTIONS
# ==========================================

results = pd.DataFrame({
    "Actual": y_test.values,
    "Predicted": np.round(predictions, 2)
})

print()
print("Sample predictions:")
print(results.head(10))


# ==========================================
# 12. SAVE MODEL
# ==========================================

model_path = "ml/model/demand_model.pkl"

joblib.dump(model, model_path)

print()
print("Model saved to:", model_path)