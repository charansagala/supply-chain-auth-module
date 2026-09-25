"""
routes/users.py
----------------
User management endpoints. All of these are ADMIN-only, per the spec:
  GET    /users             -> list all users
  GET    /users/{id}        -> view one user
  PUT    /users/{id}/role   -> change a user's role
  DELETE /users/{id}        -> delete a user
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import UserResponse, UserRoleUpdate
from dependencies.auth import require_role
from services.auth_service import get_user_by_id

router = APIRouter(prefix="/users", tags=["User Management (Admin only)"])


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List all users (ADMIN only)",
)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    return db.query(User).all()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a single user by id (ADMIN only)",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return user


@router.put(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Change a user's role (ADMIN only)",
)
def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (ADMIN only)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    # Simple safety check: don't let an admin delete their own account
    # by accident while logged in with it.
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account while logged in.",
        )

    db.delete(user)
    db.commit()
    return None
