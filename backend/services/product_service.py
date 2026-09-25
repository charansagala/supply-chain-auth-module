"""
services/product_service.py
-----------------------------
Business-logic layer for Product management.

Keeps database queries and validation rules separate from the route handlers
so the code is easier to test and reuse.

Module 2 — Order & Inventory Data Management
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.product import Product
from models.order import Order
from models.inventory import Inventory
from schemas.product import ProductCreate, ProductUpdate, ProductSummaryResponse


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    """Return the product row or None."""
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_name(db: Session, name: str) -> Optional[Product]:
    """Return the product row matching the name (case-sensitive), or None."""
    return db.query(Product).filter(Product.name == name).first()


def get_all_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    return db.query(Product).offset(skip).limit(limit).all()


def create_product(db: Session, data: ProductCreate) -> Product:
    """
    Create a new product.
    Raises 409 Conflict if a product with the same name already exists.
    """
    if get_product_by_name(db, data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A product named '{data.name}' already exists.",
        )

    product = Product(
        name=data.name,
        description=data.description,
        category=data.category,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    """
    Apply a partial update to an existing product.
    Raises 404 if the product doesn't exist.
    Raises 409 if the new name clashes with another product.
    """
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found.",
        )

    if data.name is not None:
        existing = get_product_by_name(db, data.name)
        if existing and existing.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A product named '{data.name}' already exists.",
            )
        product.name = data.name

    if data.description is not None:
        product.description = data.description

    if data.category is not None:
        product.category = data.category

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    """
    Delete a product.
    Raises 404 if it doesn't exist.
    Note: related Order/Inventory rows are cascade-deleted by the FK constraint.
    """
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found.",
        )
    db.delete(product)
    db.commit()


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def get_product_summary(db: Session, product_id: int) -> ProductSummaryResponse:
    """
    Return aggregated order and inventory statistics for one product.
    """
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found.",
        )

    # Order aggregation
    order_agg = (
        db.query(
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.quantity), 0).label("total_ordered"),
        )
        .filter(Order.product_id == product_id)
        .one()
    )

    # Inventory aggregation
    inv_agg = (
        db.query(
            func.count(Inventory.id).label("inv_count"),
            func.coalesce(func.sum(Inventory.units_sold), 0).label("total_sold"),
        )
        .filter(Inventory.product_id == product_id)
        .one()
    )

    # Latest inventory level
    latest_inv = (
        db.query(Inventory.inventory_level)
        .filter(Inventory.product_id == product_id)
        .order_by(Inventory.inventory_date.desc())
        .first()
    )

    return ProductSummaryResponse(
        product_id=product.id,
        product_name=product.name,
        total_units_sold=float(inv_agg.total_sold),
        total_units_ordered=float(order_agg.total_ordered),
        latest_inventory_level=float(latest_inv[0]) if latest_inv else None,
        order_count=int(order_agg.order_count),
        inventory_record_count=int(inv_agg.inv_count),
    )
