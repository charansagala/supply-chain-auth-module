"""
models/location.py
-------------------
SQLAlchemy ORM model for the `locations` table.

A Location represents a physical site (store, warehouse, distribution
centre) in the supply chain.  Orders and Inventory records link back
to a location via a foreign key.

Module 2 — Order & Inventory Data Management
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Location(Base):
    """Represents a supply-chain site (store, warehouse, etc.)."""

    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Unique short name / code used in the dataset (e.g. "Store_1").
    name = Column(String(255), nullable=False, unique=True, index=True)

    city = Column(String(150), nullable=True)
    state = Column(String(150), nullable=True)
    country = Column(String(150), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    orders = relationship("Order", back_populates="location")
    inventory_records = relationship("Inventory", back_populates="location")

    def __repr__(self):
        return f"<Location id={self.id} name={self.name!r}>"
