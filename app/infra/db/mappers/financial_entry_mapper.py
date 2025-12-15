"""Mapper entre FinancialEntry (domínio) e FinancialEntryModel (ORM)."""

from decimal import Decimal
from uuid import UUID

from app.domain.entities.financial_entry import EntryStatus, FinancialEntry
from app.infra.db.models.financial_entry_model import FinancialEntryModel


class FinancialEntryMapper:
    """Converte entre FinancialEntry e FinancialEntryModel."""

    @staticmethod
    def to_model(entity: FinancialEntry) -> FinancialEntryModel:
        """Converte entidade de domínio para model ORM."""
        return FinancialEntryModel(
            id=str(entity.id),
            session_id=str(entity.session_id),
            patient_id=str(entity.patient_id),
            amount=entity.amount,
            entry_date=entity.entry_date,
            description=entity.description,
            status=entity.status.value,
            created_at=entity.created_at,
            paid_at=entity.paid_at,
        )

    @staticmethod
    def to_entity(model: FinancialEntryModel) -> FinancialEntry:
        """Converte model ORM para entidade de domínio."""
        entry = object.__new__(FinancialEntry)
        object.__setattr__(entry, "id", UUID(model.id))
        object.__setattr__(entry, "session_id", UUID(model.session_id))
        object.__setattr__(entry, "patient_id", UUID(model.patient_id))
        object.__setattr__(entry, "amount", Decimal(str(model.amount)))
        object.__setattr__(entry, "entry_date", model.entry_date)
        object.__setattr__(entry, "description", model.description)
        object.__setattr__(entry, "status", EntryStatus(model.status))
        object.__setattr__(entry, "created_at", model.created_at)
        object.__setattr__(entry, "paid_at", model.paid_at)
        return entry

    @staticmethod
    def update_model(
        model: FinancialEntryModel, entity: FinancialEntry
    ) -> FinancialEntryModel:
        """Atualiza model existente com dados da entidade."""
        model.amount = entity.amount
        model.entry_date = entity.entry_date
        model.description = entity.description
        model.status = entity.status.value
        model.paid_at = entity.paid_at
        return model
