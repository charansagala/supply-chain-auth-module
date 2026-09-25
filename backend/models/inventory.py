"""
models/inventory.py
--------------------
SQLAlchemy ORM model for the `inventory` table.

An Inventory record is a daily snapshot of stock levels for a product
at a specific location.  It also captures units sold and units ordered
for that day, making it the richest table for historical demand analysis.

Dataset column mapping
----------------------
The Kaggle "Supply Chain Demand Forecasting" dataset typically contains:
    Date              → inventory_date
    Product ID        → product_id   (FK → products.id)
    Store ID          → location_id  (FK → locations.id)
    Inventory Level   → inventory_level
    Units Sold        → units_sold
    Units Ordered     → units_ordered
    Demand Forecast   → demand_forecast  (stored for reference; NOT used
                         for ML in this module — that belongs to Module 3)

If the dataset does NOT contain Demand Forecast, that column is NULL.

Module 2 — Order & Inventory Data Management
"""

from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Inventory(Base):
    """Daily inventory snapshot for a product × location pair."""

    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    location_id = Column(
        Integer,
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    inventory_date = Column(Date, nullable=False, index=True)

    # Stock on hand at the end of the day (can be 0 but not negative unless
    # the source dataset itself contains negative values).
    inventory_level = Column(Float, nullable=False)

    # Demand (units sold) recorded for this day.
    units_sold = Column(Float, nullable=True)

    # Replenishment units ordered on this day.
    units_ordered = Column(Float, nullable=True)

    # Demand forecast value from the dataset (stored as-is; forecasting
    # logic lives in Module 3).
    demand_forecast = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="inventory_records")
    location = relationship("Location", back_populates="inventory_records")

    # Composite index for efficient range queries.
    __table_args__ = (
        Index(
            "ix_inventory_product_location_date",
            "product_id",
            "location_id",
            "inventory_date",
        ),
    )

    def __repr__(self):
        return (
            f"<Inventory id={self.id} product_id={self.product_id} "
            f"location_id={self.location_id} date={self.inventory_date} "
            f"level={self.inventory_level}>"
        )
