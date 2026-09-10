from sqlalchemy import Column, Integer, String, Numeric, DateTime
from backend.core.database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(150), nullable=False)

    category_id = Column(Integer, nullable=True)
    supplier_id = Column(Integer, nullable=True)

    unit = Column(String(30), nullable=False, default="unit")

    cost_price = Column(Numeric(12, 2), nullable=False, default=0.00)
    selling_price = Column(Numeric(12, 2), nullable=False, default=0.00)

    current_stock = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=0)
    safety_stock = Column(Integer, nullable=False, default=0)

    is_active = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)