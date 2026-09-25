"""
services/order_service.py
---------------------------
Business-logic layer for Order management.

Module 2 — Order & Inventory Data Management
"""

from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.order import Order
from models.product import Product
from models.location import Location
from schemas.order import OrderCreate, OrderUpdate, OrderSummaryResponse


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

def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders(
    db: Session,
    product_id: Optional[int] = None,
    location_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Order]:
    """
    Return orders with optional filters.
    All filter parameters are independently composable.
    """
    query = db.query(Order)

    if product_id is not None:
        query = query.filter(Order.product_id == product_id)
    if location_id is not None:
        query = query.filter(Order.location_id == location_id)
    if start_date is not None:
        query = query.filter(Order.order_date >= start_date)
    if end_date is not None:
        query = query.filter(Order.order_date <= end_date)

    return query.order_by(Order.order_date.desc()).offset(skip).limit(limit).all()


def create_order(db: Session, data: OrderCreate) -> Order:
    """
    Create a new order record.
    Validates that the referenced product and location exist.
    """
    _assert_product_exists(db, data.product_id)
    _assert_location_exists(db, data.location_id)

    order = Order(
        product_id=data.product_id,
        location_id=data.location_id,
        order_date=data.order_date,
        quantity=data.quantity,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def update_order(db: Session, order_id: int, data: OrderUpdate) -> Order:
    """Partial update for an existing order."""
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id={order_id} not found.",
        )

    if data.order_date is not None:
        order.order_date = data.order_date
    if data.quantity is not None:
        order.quantity = data.quantity

    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order_id: int) -> None:
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id={order_id} not found.",
        )
    db.delete(order)
    db.commit()


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def get_orders_summary(db: Session) -> OrderSummaryResponse:
    """Global aggregation across all order records."""
    result = db.query(
        func.count(Order.id).label("total_orders"),
        func.coalesce(func.sum(Order.quantity), 0).label("total_quantity"),
        func.count(func.distinct(Order.product_id)).label("unique_products"),
        func.count(func.distinct(Order.location_id)).label("unique_locations"),
    ).one()

    return OrderSummaryResponse(
        total_orders=int(result.total_orders),
        total_quantity=float(result.total_quantity),
        unique_products=int(result.unique_products),
        unique_locations=int(result.unique_locations),
    )
