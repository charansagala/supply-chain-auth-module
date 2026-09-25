"""
services/inventory_service.py
-------------------------------
Business-logic layer for Inventory management.

Module 2 — Order & Inventory Data Management
"""

from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.inventory import Inventory
from models.product import Product
from models.location import Location
from schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventorySummaryResponse,
    InventoryByProductResponse,
    InventoryByLocationResponse,
)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _assert_product_exists(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found.",
        )
    return product


def _assert_location_exists(db: Session, location_id: int) -> Location:
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id={location_id} not found.",
        )
    return location


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def get_inventory_by_id(db: Session, inventory_id: int) -> Optional[Inventory]:
    return db.query(Inventory).filter(Inventory.id == inventory_id).first()


def get_inventory(
    db: Session,
    product_id: Optional[int] = None,
    location_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Inventory]:
    """Return inventory records with optional composable filters."""
    query = db.query(Inventory)

    if product_id is not None:
        query = query.filter(Inventory.product_id == product_id)
    if location_id is not None:
        query = query.filter(Inventory.location_id == location_id)
    if start_date is not None:
        query = query.filter(Inventory.inventory_date >= start_date)
    if end_date is not None:
        query = query.filter(Inventory.inventory_date <= end_date)

    return (
        query.order_by(Inventory.inventory_date.desc()).offset(skip).limit(limit).all()
    )


def create_inventory(db: Session, data: InventoryCreate) -> Inventory:
    """
    Create a new inventory snapshot record.
    Validates referenced product and location.
    """
    _assert_product_exists(db, data.product_id)
    _assert_location_exists(db, data.location_id)

    record = Inventory(
        product_id=data.product_id,
        location_id=data.location_id,
        inventory_date=data.inventory_date,
        inventory_level=data.inventory_level,
        units_sold=data.units_sold,
        units_ordered=data.units_ordered,
        demand_forecast=data.demand_forecast,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_inventory(db: Session, inventory_id: int, data: InventoryUpdate) -> Inventory:
    """Partial update for an existing inventory record."""
    record = get_inventory_by_id(db, inventory_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory record with id={inventory_id} not found.",
        )

    for field in ("inventory_date", "inventory_level", "units_sold", "units_ordered", "demand_forecast"):
        val = getattr(data, field)
        if val is not None:
            setattr(record, field, val)

    db.commit()
    db.refresh(record)
    return record


def delete_inventory(db: Session, inventory_id: int) -> None:
    record = get_inventory_by_id(db, inventory_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory record with id={inventory_id} not found.",
        )
    db.delete(record)
    db.commit()


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def get_inventory_summary(db: Session) -> InventorySummaryResponse:
    """Global aggregation across all inventory records."""
    result = db.query(
        func.count(Inventory.id).label("total_records"),
        func.coalesce(func.sum(Inventory.units_sold), 0).label("total_sold"),
        func.coalesce(func.sum(Inventory.units_ordered), 0).label("total_ordered"),
        func.coalesce(func.avg(Inventory.inventory_level), 0).label("avg_level"),
        func.count(func.distinct(Inventory.product_id)).label("unique_products"),
        func.count(func.distinct(Inventory.location_id)).label("unique_locations"),
    ).one()

    return InventorySummaryResponse(
        total_records=int(result.total_records),
        total_units_sold=float(result.total_sold),
        total_units_ordered=float(result.total_ordered),
        average_inventory_level=float(result.avg_level),
        unique_products=int(result.unique_products),
        unique_locations=int(result.unique_locations),
    )


def get_inventory_by_product(db: Session) -> List[InventoryByProductResponse]:
    """Aggregate inventory stats grouped by product."""
    rows = (
        db.query(
            Inventory.product_id,
            Product.name.label("product_name"),
            func.coalesce(func.sum(Inventory.units_sold), 0).label("total_sold"),
            func.coalesce(func.sum(Inventory.units_ordered), 0).label("total_ordered"),
            func.count(Inventory.id).label("record_count"),
        )
        .join(Product, Product.id == Inventory.product_id)
        .group_by(Inventory.product_id, Product.name)
        .all()
    )

    # Fetch latest inventory level for each product separately (avoids
    # complex window-function syntax for SQLite/MySQL compatibility).
    results = []
    for row in rows:
        latest = (
            db.query(Inventory.inventory_level)
            .filter(Inventory.product_id == row.product_id)
            .order_by(Inventory.inventory_date.desc())
            .first()
        )
        results.append(
            InventoryByProductResponse(
                product_id=row.product_id,
                product_name=row.product_name,
                total_units_sold=float(row.total_sold),
                total_units_ordered=float(row.total_ordered),
                latest_inventory_level=float(latest[0]) if latest else None,
                record_count=int(row.record_count),
            )
        )
    return results


def get_inventory_by_location(db: Session) -> List[InventoryByLocationResponse]:
    """Aggregate inventory stats grouped by location."""
    rows = (
        db.query(
            Inventory.location_id,
            Location.name.label("location_name"),
            func.coalesce(func.sum(Inventory.units_sold), 0).label("total_sold"),
            func.coalesce(func.sum(Inventory.units_ordered), 0).label("total_ordered"),
            func.count(Inventory.id).label("record_count"),
        )
        .join(Location, Location.id == Inventory.location_id)
        .group_by(Inventory.location_id, Location.name)
        .all()
    )

    results = []
    for row in rows:
        latest = (
            db.query(Inventory.inventory_level)
            .filter(Inventory.location_id == row.location_id)
            .order_by(Inventory.inventory_date.desc())
            .first()
        )
        results.append(
            InventoryByLocationResponse(
                location_id=row.location_id,
                location_name=row.location_name,
                total_units_sold=float(row.total_sold),
                total_units_ordered=float(row.total_ordered),
                latest_inventory_level=float(latest[0]) if latest else None,
                record_count=int(row.record_count),
            )
        )
    return results
