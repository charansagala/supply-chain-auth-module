"""
models/user.py
---------------
Defines the `User` table using SQLAlchemy's ORM.

Each attribute on the class (id, full_name, email, ...) becomes a column
in the "users" table in the database (SQLite for development, MySQL for production).
"""

import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func

from database import Base


class RoleEnum(str, enum.Enum):
    """
    The three roles allowed in this system.

    Inheriting from `str` as well as `enum.Enum` means these values behave
    like normal strings ("ADMIN", "MANAGER", "PLANNER") which makes them
    easy to use in Pydantic schemas and JWT payloads.
    """
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    PLANNER = "PLANNER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    full_name = Column(String(150), nullable=False)

    # unique=True ensures the database rejects duplicate emails at the DB level too,
    # not just in our application code.
    email = Column(String(150), unique=True, index=True, nullable=False)

    # We NEVER store the raw password. Only its bcrypt hash.
    password_hash = Column(String(255), nullable=False)

    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.PLANNER)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"
