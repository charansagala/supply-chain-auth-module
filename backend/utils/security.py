"""
utils/security.py
------------------
Low-level security helpers used across the app:
  - hashing / verifying passwords with bcrypt
  - creating / decoding JWT access tokens

Nothing in this file knows about FastAPI routes or the database — it's
pure, reusable logic. This separation makes the code easier to test and
easier to explain in a project presentation.
"""

import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY is not set. Did you create a .env file from .env.example?"
    )

# CryptContext handles bcrypt hashing for us. "bcrypt" is the recommended
# scheme for password storage — it's slow on purpose, which makes
# brute-force attacks harder.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------

def hash_password(plain_password: str) -> str:
    """Turn a plain-text password into a secure bcrypt hash before saving it."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plain-text password (from login) against the stored hash."""
    return pwd_context.verify(plain_password, password_hash)


# ---------------------------------------------------------------------
# JWT tokens
# ---------------------------------------------------------------------

def create_access_token(user_id: int, email: str, role: str) -> str:
    """
    Build a signed JWT that encodes who the user is.

    The token contains:
      - sub  : the user's id (as a string, per JWT convention)
      - email: the user's email (handy for debugging / display)
      - role : the user's role, used later for authorization checks
      - exp  : expiry timestamp, after which the token is no longer valid
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": expire,
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    """
    Verify a JWT's signature and expiry, and return its payload.
    Raises jose.JWTError if the token is invalid, tampered with, or expired.
    """
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return payload
