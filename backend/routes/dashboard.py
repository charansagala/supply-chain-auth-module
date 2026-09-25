"""
routes/dashboard.py
--------------------
Placeholder dashboard endpoints that demonstrate multi-role access control.
These will eventually be replaced/extended by the real Analytics Dashboard
and Demand Forecasting modules — for now they just prove that role checks
work correctly:

  GET /manager/dashboard  -> ADMIN and MANAGER
  GET /planner/dashboard  -> ADMIN and PLANNER
"""

from fastapi import APIRouter, Depends

from models.user import User
from dependencies.auth import require_role

router = APIRouter(tags=["Dashboards (demo of role-based access)"])


@router.get("/manager/dashboard", summary="Manager dashboard (ADMIN + MANAGER)")
def manager_dashboard(current_user: User = Depends(require_role("ADMIN", "MANAGER"))):
    """
    In later modules this will return real analytics/forecast data.
    For now it just confirms who is allowed in.
    """
    return {
        "message": f"Welcome {current_user.full_name}, this is the manager dashboard.",
        "role": current_user.role.value,
        "available_soon": [
            "Demand forecasts",
            "Analytics dashboards",
            "Inventory information",
            "Procurement recommendations",
            "Forecast anomaly monitoring",
        ],
    }


@router.get("/planner/dashboard", summary="Planner dashboard (ADMIN + PLANNER)")
def planner_dashboard(current_user: User = Depends(require_role("ADMIN", "PLANNER"))):
    """
    In later modules this will return real forecast/inventory data.
    For now it just confirms who is allowed in.
    """
    return {
        "message": f"Welcome {current_user.full_name}, this is the planner dashboard.",
        "role": current_user.role.value,
        "available_soon": [
            "Demand forecasts",
            "Inventory information",
            "Procurement recommendations",
            "Inventory alerts",
        ],
    }
