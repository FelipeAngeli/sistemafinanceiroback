"""Model SQLAlchemy para Session."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from app.infra.db.models import PatientModel, UserModel
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.models.base import Base


class SessionModel(Base):
    """Tabela de sessões."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="agendada", nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships (opcional, para queries mais fáceis)
    user: Mapped["UserModel"] = relationship(
        "UserModel", backref="sessions", lazy="selectin"
    )
    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", backref="sessions", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<SessionModel(id={self.id}, status={self.status})>"
