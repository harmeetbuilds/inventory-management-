import pandas as pd
from database import get_connection


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

print(df)