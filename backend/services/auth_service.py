"""
services/auth_service.py
-------------------------
This is the "business logic" layer, sitting between the routes (API layer)
and the database (models). Keeping this logic separate from the routes
makes the code easier to read, reuse, and test.
"""

from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User
from schemas.user import UserCreate
from utils.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def register_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user account.
    Raises a 400 error if the email is already registered.
    """
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    new_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role=user_in.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # reloads the row so new_user.id / created_at are populated
    return new_user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Verify email + password. Raises a 401 error if either is wrong.
    We intentionally use the SAME error message for "no such user" and
    "wrong password" so attackers can't use the error to guess valid emails.
    """
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    return user
