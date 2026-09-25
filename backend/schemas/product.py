"""
schemas/product.py
-------------------
Pydantic schemas for Product request / response validation.

Module 2 — Order & Inventory Data Management
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Request schemas (incoming data)
# ---------------------------------------------------------------------------

class ProductCreate(BaseModel):
    """Body required to create a new product (ADMIN only)."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique product name or SKU code.",
        examples=["Widget A"],
    )
    description: Optional[str] = Field(
        None,
        description="Optional free-text description.",
        examples=["Standard widget for retail use."],
    )
    category: Optional[str] = Field(
        None,
        max_length=100,
        description="Product category (e.g. Electronics, Apparel).",
        examples=["Electronics"],
    )


class ProductUpdate(BaseModel):
    """Body for a partial update — all fields are optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)


# ---------------------------------------------------------------------------
# Response schemas (outgoing data)
# ---------------------------------------------------------------------------

class ProductResponse(BaseModel):
    """Returned when a product is created, fetched, or updated."""

    id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductSummaryResponse(BaseModel):
    """Aggregated statistics for a single product."""

    product_id: int
    product_name: str
    total_units_sold: float
    total_units_ordered: float
    latest_inventory_level: Optional[float]
    order_count: int
    inventory_record_count: int
