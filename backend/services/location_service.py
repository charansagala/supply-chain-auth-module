"""
services/location_service.py
------------------------------
Business-logic layer for Location management.

Module 2 — Order & Inventory Data Management
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.location import Location
from models.order import Order
from models.inventory import Inventory
from schemas.location import LocationCreate, LocationUpdate, LocationSummaryResponse


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def get_location_by_id(db: Session, location_id: int) -> Optional[Location]:
    return db.query(Location).filter(Location.id == location_id).first()


def get_location_by_name(db: Session, name: str) -> Optional[Location]:
    return db.query(Location).filter(Location.name == name).first()


def get_all_locations(db: Session, skip: int = 0, limit: int = 100) -> List[Location]:
    return db.query(Location).offset(skip).limit(limit).all()


def create_location(db: Session, data: LocationCreate) -> Location:
    """
    Create a new location.
    Raises 409 if a location with the same name already exists.
    """
    if get_location_by_name(db, data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A location named '{data.name}' already exists.",
        )

    location = Location(
        name=data.name,
        city=data.city,
        state=data.state,
        country=data.country,
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


def update_location(db: Session, location_id: int, data: LocationUpdate) -> Location:
    location = get_location_by_id(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id={location_id} not found.",
        )

    if data.name is not None:
        existing = get_location_by_name(db, data.name)
        if existing and existing.id != location_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A location named '{data.name}' already exists.",
            )
        location.name = data.name

    for field in ("city", "state", "country"):
        val = getattr(data, field)
        if val is not None:
            setattr(location, field, val)

    db.commit()
    db.refresh(location)
    return location


def delete_location(db: Session, location_id: int) -> None:
    location = get_location_by_id(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id={location_id} not found.",
        )
    db.delete(location)
    db.commit()


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def get_location_summary(db: Session, location_id: int) -> LocationSummaryResponse:
    """Aggregated order and inventory stats for one location."""
    location = get_location_by_id(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id={location_id} not found.",
        )

    order_agg = (
        db.query(
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.quantity), 0).label("total_ordered"),
        )
        .filter(Order.location_id == location_id)
        .one()
    )

    inv_agg = (
        db.query(
            func.count(Inventory.id).label("inv_count"),
            func.coalesce(func.sum(Inventory.units_sold), 0).label("total_sold"),
        )
        .filter(Inventory.location_id == location_id)
        .one()
    )

    latest_inv = (
        db.query(Inventory.inventory_level)
        .filter(Inventory.location_id == location_id)
        .order_by(Inventory.inventory_date.desc())
        .first()
    )

    return LocationSummaryResponse(
        location_id=location.id,
        location_name=location.name,
        total_units_sold=float(inv_agg.total_sold),
        total_units_ordered=float(order_agg.total_ordered),
        latest_inventory_level=float(latest_inv[0]) if latest_inv else None,
        order_count=int(order_agg.order_count),
        inventory_record_count=int(inv_agg.inv_count),
    )
