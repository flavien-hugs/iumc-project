import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum as SaEnum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    content_admin = "content_admin"
    sales_agent = "sales_agent"
    branch_manager = "branch_manager"
    viewer = "viewer"


class User(Base):
    # Pluriel : "user" est un identifiant réservé de PostgreSQL.
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SaEnum(UserRole, name="user_role"))
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL")
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Suppression logique : distincte de `is_active` (qui reste le
    # suspendre/réactiver réversible au quotidien). Un compte supprimé garde
    # ses données (historique, logs) mais devient invisible/immuable par
    # défaut, jusqu'à restauration explicite.
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def is_usable(self) -> bool:
        """Compte ni suspendu ni supprimé — condition unique pour toute
        vérification d'accès (authentification, affectation, etc.)."""
        return self.is_active and self.deleted_at is None


class PasswordResetToken(Base):
    """Password reset token, hashed before storage (ADR-0012)."""

    __tablename__ = "password_reset_token"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(255), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_used: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
