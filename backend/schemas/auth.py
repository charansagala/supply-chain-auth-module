"""
schemas/auth.py
----------------
Schemas related to logging in and JWT tokens.
"""

from pydantic import BaseModel, EmailStr, Field

from schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Shape of the JSON body expected when a user logs in."""
    email: EmailStr = Field(..., examples=["charan@example.com"])
    password: str = Field(..., examples=["StrongPass123"])


class TokenResponse(BaseModel):
    """
    Shape of the JSON we send back after a successful login.
    Contains the JWT plus basic user info, as required by the project spec.
    """
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    """
    Shape of the data we encode INSIDE the JWT itself.
    'sub' (subject) holds the user's id, following standard JWT convention.
    """
    sub: str
    email: str
    role: str
    exp: int
