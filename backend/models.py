from sqlalchemy import Column, Float, Integer, String
from backend.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    stock_quantity = Column(Integer, default=0)
    safety_stock = Column(Integer, default=10)
    price = Column(Float, default=0.0)