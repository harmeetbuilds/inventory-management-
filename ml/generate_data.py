import random
from datetime import date, timedelta

from database import get_connection


# Products already present in our database
products = {
    1: {"base_demand": 12, "price": 700},
    2: {"base_demand": 18, "price": 900},
    3: {"base_demand": 25, "price": 180},
    4: {"base_demand": 15, "price": 90},
}


# Generate approximately one year of sales
start_date = date(2025, 8, 1)
end_date = date(2026, 8, 24)

connection = get_connection()
cursor = connection.cursor()

current_date = start_date

while current_date <= end_date:

    day_of_week = current_date.weekday()

    for product_id, product in products.items():

        # Base demand
        demand = product["base_demand"]

        # Weekend effect
        if day_of_week >= 5:
            demand *= 0.75

        # Small upward trend
        days_passed = (current_date - start_date).days
        demand *= 1 + (days_passed / 365) * 0.15

        # Random daily variation
        demand *= random.uniform(0.75, 1.25)

        quantity = max(0, round(demand))

        if quantity == 0:
            continue

        total = quantity * product["price"]

        # Create sale
        cursor.execute(
            """
            INSERT INTO sales
            (sale_date, customer_name, total_amount, status)
            VALUES (%s, %s, %s, 'COMPLETED')
            """,
            (
                current_date,
                "Synthetic Customer",
                total
            )
        )

        sale_id = cursor.lastrowid

        # Create sale item
        cursor.execute(
            """
            INSERT INTO sale_items
            (sale_id, product_id, quantity, unit_price, discount)
            VALUES (%s, %s, %s, %s, 0)
            """,
            (
                sale_id,
                product_id,
                quantity,
                product["price"]
            )
        )

    current_date += timedelta(days=1)


connection.commit()

cursor.close()
connection.close()

print("Synthetic sales data generated successfully!")