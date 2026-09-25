"""
models/product.py
------------------
SQLAlchemy ORM model for the `products` table.

A Product represents a distinct item tracked in the supply chain,
e.g. "Widget A", "Gadget Pro".  Products are referenced by both
Order and Inventory records via foreign keys.

Module 2 — Order & Inventory Data Management
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Product(Base):
    """Represents a unique supply-chain product (SKU)."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Human-readable name, must be unique so we can deduplicate CSV imports.
    name = Column(String(255), nullable=False, unique=True, index=True)

    description = Column(Text, nullable=True)

    # Free-text category, e.g. "Electronics", "Apparel".
    category = Column(String(100), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships — lazy loading is fine for a project of this size.
    orders = relationship("Order", back_populates="product")
    inventory_records = relationship("Inventory", back_populates="product")

    def __repr__(self):
        return f"<Product id={self.id} name={self.name!r}>"
