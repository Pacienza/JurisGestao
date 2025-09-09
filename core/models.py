from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    String, Integer, Boolean, DateTime, Table, Column,
    ForeignKey, UniqueConstraint, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

# --- Associação user-role ------

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

# --- RBAC: permissões e associação role-permission ---
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Perm {self.name}>"

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # RBAC: permissões do papel
    permissions: Mapped[list[Permission]] = relationship(
        secondary=role_permissions,
        backref="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("email", name="uq_users_email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    roles: Mapped[list[Role]] = relationship(
        secondary=user_roles,
        backref="users",
        lazy="selectin",   # evita unique() nas queries
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
