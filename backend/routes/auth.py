"""
routes/auth.py
---------------
Public-facing authentication endpoints:
  POST /auth/register  -> create a new account
  POST /auth/login      -> log in, receive a JWT
  GET  /auth/me          -> get the currently logged-in user's profile
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.user import UserCreate, UserResponse
from schemas.auth import LoginRequest, TokenResponse
from services.auth_service import register_user, authenticate_user
from utils.security import create_access_token
from dependencies.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user (ADMIN, MANAGER, or PLANNER)",
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Anyone can call this to create an account for the demo/project.

    In a real production system you would usually restrict who can create
    ADMIN accounts — but for this university project, registration is left
    open so it's easy to test and present.
    """
    new_user = register_user(db, user_in)
    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in with email + password, receive a JWT access token",
)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Verifies the user's credentials and returns a signed JWT plus the
    user's basic profile info, as required by the spec.
    """
    user = authenticate_user(db, credentials.email, credentials.password)

    token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value,
    )

    return TokenResponse(access_token=token, user=user)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the profile of the currently logged-in user",
)
def read_my_profile(current_user: User = Depends(get_current_user)):
    """
    Any authenticated user (ADMIN, MANAGER, or PLANNER) can call this.
    It's a good way to test that a JWT token is valid from Swagger UI.
    """
    return current_user
