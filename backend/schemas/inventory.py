"""
schemas/inventory.py
---------------------
Pydantic schemas for Inventory request / response validation.

Module 2 — Order & Inventory Data Management
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class InventoryCreate(BaseModel):
    """Body required to create a new inventory snapshot record."""

    product_id: int = Field(..., gt=0, description="ID of an existing product.")
    location_id: int = Field(..., gt=0, description="ID of an existing location.")
    inventory_date: date = Field(
        ..., description="Date of this inventory snapshot (YYYY-MM-DD)."
    )
    inventory_level: float = Field(
        ...,
        description=(
            "Stock on hand at end of day. "
            "Cannot be negative (use 0 for stockout)."
        ),
        examples=[500.0],
    )
    units_sold: Optional[float] = Field(
        None, ge=0, description="Units sold on this day.", examples=[45.0]
    )
    units_ordered: Optional[float] = Field(
        None, ge=0, description="Units replenishment-ordered on this day.", examples=[200.0]
    )
    demand_forecast: Optional[float] = Field(
        None,
        description=(
            "Demand forecast value from the source dataset, stored for reference. "
            "Forecasting logic is NOT implemented in Module 2."
        ),
        examples=[48.5],
    )

    @field_validator("inventory_level")
    @classmethod
    def inventory_not_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError(
                "inventory_level cannot be negative. Use 0 to represent a stockout."
            )
        return v

    @field_validator("units_sold", "units_ordered")
    @classmethod
    def units_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("units_sold / units_ordered cannot be negative.")
        return v


class InventoryUpdate(BaseModel):
    """Partial update for an inventory record."""

    inventory_date: Optional[date] = None
    inventory_level: Optional[float] = Field(None, ge=0)
    units_sold: Optional[float] = Field(None, ge=0)
    units_ordered: Optional[float] = Field(None, ge=0)
    demand_forecast: Optional[float] = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class InventoryResponse(BaseModel):
    """Returned when an inventory record is created or fetched."""

    id: int
    product_id: int
    location_id: int
    inventory_date: date
    inventory_level: float
    units_sold: Optional[float]
    units_ordered: Optional[float]
    demand_forecast: Optional[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventorySummaryResponse(BaseModel):
    """Aggregated inventory statistics — returned by GET /inventory/summary."""

    total_records: int
    total_units_sold: float
    total_units_ordered: float
    average_inventory_level: float
    unique_products: int
    unique_locations: int


class InventoryByProductResponse(BaseModel):
    """Per-product inventory aggregation."""

    product_id: int
    product_name: str
    latest_inventory_level: Optional[float]
    total_units_sold: float
    total_units_ordered: float
    record_count: int


class InventoryByLocationResponse(BaseModel):
    """Per-location inventory aggregation."""

    location_id: int
    location_name: str
    latest_inventory_level: Optional[float]
    total_units_sold: float
    total_units_ordered: float
    record_count: int
