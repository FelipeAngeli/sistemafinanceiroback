"""Model SQLAlchemy para FinancialEntry."""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.models.base import Base


class FinancialEntryModel(Base):
    """Tabela de lançamentos financeiros."""

    __tablename__ = "financial_entries"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sessions.id"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="pendente", nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel", backref="financial_entries", lazy="selectin"
    )
    session: Mapped["SessionModel"] = relationship(
        "SessionModel", backref="financial_entries", lazy="selectin"
    )
    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", backref="financial_entries", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<FinancialEntryModel(id={self.id}, amount={self.amount}, status={self.status})>"
