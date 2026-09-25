"""
models/order.py
----------------
SQLAlchemy ORM model for the `orders` table.

An Order record captures the quantity of a product ordered at a given
location on a particular date.  This is the core transactional table
for demand history.

Dataset column mapping
----------------------
The Kaggle "Supply Chain Demand Forecasting" dataset typically contains
columns such as:
    Date         → order_date
    Product ID   → product_id  (FK → products.id)
    Store ID     → location_id (FK → locations.id)
    Units Ordered → quantity

Module 2 — Order & Inventory Data Management
"""

from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Order(Base):
    """One historical order record: product × location × date × quantity."""

    __tablename__ = "orders"

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

    # Calendar date of the order (no time component needed for daily records).
    order_date = Column(Date, nullable=False, index=True)

    # Units ordered — stored as Float to accommodate partial-unit datasets.
    quantity = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="orders")
    location = relationship("Location", back_populates="orders")

    # Composite index for the most common query pattern: filter by product,
    # location, and a date range.
    __table_args__ = (
        Index("ix_orders_product_location_date", "product_id", "location_id", "order_date"),
    )

    def __repr__(self):
        return (
            f"<Order id={self.id} product_id={self.product_id} "
            f"location_id={self.location_id} date={self.order_date}>"
        )
