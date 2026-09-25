"""
schemas/user.py
----------------
Pydantic schemas control what data comes IN to our API (request bodies)
and what data goes OUT (response bodies). FastAPI uses these to validate
incoming JSON automatically and to generate the Swagger UI docs.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from models.user import RoleEnum


class UserCreate(BaseModel):
    """Shape of the JSON body expected when a new user registers."""
    full_name: str = Field(..., min_length=2, max_length=150, examples=["Sagala Charan"])
    email: EmailStr = Field(..., examples=["charan@example.com"])
    password: str = Field(..., min_length=6, max_length=100, examples=["StrongPass123"])
    role: RoleEnum = Field(..., examples=["PLANNER"])


class UserResponse(BaseModel):
    """
    Shape of the JSON we send back for a user.
    Notice password_hash is NOT included here — we never expose it.
    """
    id: int
    full_name: str
    email: EmailStr
    role: RoleEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Allows Pydantic to read data directly from SQLAlchemy model objects
    # (instead of only from dicts).
    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    """Body for PUT /users/{id}/role — admin changes another user's role."""
    role: RoleEnum
