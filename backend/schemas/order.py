"""
schemas/order.py
-----------------
Pydantic schemas for Order request / response validation.

Module 2 — Order & Inventory Data Management
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class OrderCreate(BaseModel):
    """Body required to create a new order record."""

    product_id: int = Field(..., gt=0, description="ID of an existing product.")
    location_id: int = Field(..., gt=0, description="ID of an existing location.")
    order_date: date = Field(..., description="Calendar date of the order (YYYY-MM-DD).")
    quantity: float = Field(
        ...,
        ge=0,
        description="Units ordered. Must be zero or positive.",
        examples=[150.0],
    )

    @field_validator("quantity")
    @classmethod
    def quantity_not_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Quantity cannot be negative.")
        return v


class OrderUpdate(BaseModel):
    """Partial update for an order record."""

    order_date: Optional[date] = None
    quantity: Optional[float] = Field(None, ge=0)

    @field_validator("quantity")
    @classmethod
    def quantity_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Quantity cannot be negative.")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class OrderResponse(BaseModel):
    """Returned when an order is created or fetched."""

    id: int
    product_id: int
    location_id: int
    order_date: date
    quantity: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderSummaryResponse(BaseModel):
    """Aggregated order totals — returned by GET /orders/summary."""

    total_orders: int
    total_quantity: float
    unique_products: int
    unique_locations: int
