"""
dependencies/auth.py
---------------------
Reusable FastAPI "dependencies" for protecting routes.

  - get_current_user : decodes the JWT from the Authorization header and
                        loads the matching user from the database. Use this
                        on ANY route that requires the caller to be logged in.

  - require_role(...) : builds on top of get_current_user to additionally
                         check that the user's role is one of the allowed
                         roles for that route. Use this for role-restricted
                         routes like "ADMIN only".

These are used with FastAPI's `Depends()` system, e.g.:

    @router.get("/users")
    def list_users(current_user: User = Depends(require_role("ADMIN"))):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from utils.security import decode_access_token

# This tells FastAPI (and Swagger UI) that clients should send the token as:
#   Authorization: Bearer <token>
# tokenUrl points Swagger's "Authorize" button at our login endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decodes the JWT sent in the Authorization header and returns the
    matching User row from the database. Any route that depends on this
    is automatically protected — no token (or an invalid/expired one)
    results in a 401 error.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        # Covers expired tokens, tampered signatures, malformed tokens, etc.
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    return user


def require_role(*allowed_roles: str):
    """
    Factory function that builds a dependency restricting a route to
    specific roles.

    Example:
        Depends(require_role("ADMIN"))                # ADMIN only
        Depends(require_role("ADMIN", "MANAGER"))      # ADMIN or MANAGER
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{current_user.role.value}' is not permitted to "
                    f"access this resource. Allowed roles: {', '.join(allowed_roles)}."
                ),
            )
        return current_user

    return role_checker
