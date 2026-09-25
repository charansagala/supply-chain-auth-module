"""
schemas/location.py
--------------------
Pydantic schemas for Location request / response validation.

Module 2 — Order & Inventory Data Management
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class LocationCreate(BaseModel):
    """Body required to create a new location (ADMIN only)."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique location name or code, e.g. 'Store_1' or 'Warehouse_East'.",
        examples=["Store_1"],
    )
    city: Optional[str] = Field(None, max_length=150, examples=["New York"])
    state: Optional[str] = Field(None, max_length=150, examples=["NY"])
    country: Optional[str] = Field(None, max_length=150, examples=["USA"])


class LocationUpdate(BaseModel):
    """Partial update — all fields optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, max_length=150)
    state: Optional[str] = Field(None, max_length=150)
    country: Optional[str] = Field(None, max_length=150)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class LocationResponse(BaseModel):
    """Returned when a location is created, fetched, or updated."""

    id: int
    name: str
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LocationSummaryResponse(BaseModel):
    """Aggregated statistics for a single location."""

    location_id: int
    location_name: str
    total_units_sold: float
    total_units_ordered: float
    latest_inventory_level: Optional[float]
    order_count: int
    inventory_record_count: int
