"""
main.py
-------
Entry point of the FastAPI application.

Responsibilities:
  1. Create the FastAPI app instance.
  2. Create all database tables on startup (if they don't already exist).
  3. Wire up (include) all the route modules.

Run this file with:
    uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from models import user  # noqa: F401  (import ensures the User model is registered with Base)
from routes import auth, users, dashboard

# Creates all tables defined by models that inherit from Base,
# ONLY if they don't already exist. Safe to run every time the app starts.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Supply Chain Demand Forecasting System",
    description=(
        "Module 1: Authentication & Role Management. "
        "Provides registration, login (JWT), and role-based access control "
        "for ADMIN, MANAGER, and PLANNER users."
    ),
    version="1.0.0",
)

# Allow the frontend (served from a different origin/port, e.g. a static
# file server on :5500 or :3000) to call this API from the browser.
# For a university project, allowing all origins keeps setup simple.
# In production you would restrict this to your actual frontend's URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route groups. Each router already has its own prefix/tags
# defined inside its file (e.g. auth.py uses prefix="/auth").
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health Check"], summary="Basic health check")
def read_root():
    """Simple endpoint to confirm the API is running."""
    return {
        "status": "ok",
        "service": "Supply Chain Demand Forecasting System - Auth Module",
        "docs": "/docs",
    }
