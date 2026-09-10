import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

# Project root
BASE_DIR = Path(__file__).resolve().parents[2]

# Database configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# Encode password safely for MySQL URL
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:3306/{DB_NAME}"
)

# ML model path
MODEL_PATH = BASE_DIR / "ml" / "model" / "demand_model.pkl"


class Settings:
    DATABASE_URL = DATABASE_URL
    MODEL_PATH = MODEL_PATH


settings = Settings()