import mysql.connector
from mysql.connector import pooling
from backend.core.config import settings

def get_db():
    connection = mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )
    try:
        yield connection
    finally:
        connection.close()