"""Mapper entre Session (domínio) e SessionModel (ORM)."""

from decimal import Decimal
from uuid import UUID

from app.domain.entities.session import Session, SessionStatus
from app.infra.db.models.session_model import SessionModel


class SessionMapper:
    """Converte entre Session e SessionModel."""

    @staticmethod
    def to_model(entity: Session) -> SessionModel:
        """Converte entidade de domínio para model ORM."""
        return SessionModel(
            id=str(entity.id),
            user_id=str(entity.user_id),
            patient_id=str(entity.patient_id),
            date_time=entity.date_time,
            duration_minutes=entity.duration_minutes,
            price=entity.price,
            status=entity.status.value,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(model: SessionModel) -> Session:
        """Converte model ORM para entidade de domínio."""
        session = object.__new__(Session)
        object.__setattr__(session, "id", UUID(model.id))
        object.__setattr__(session, "user_id", UUID(model.user_id))
        object.__setattr__(session, "patient_id", UUID(model.patient_id))
        object.__setattr__(session, "date_time", model.date_time)
        object.__setattr__(session, "duration_minutes", model.duration_minutes)
        object.__setattr__(session, "price", Decimal(str(model.price)))
        object.__setattr__(session, "status", SessionStatus(model.status))
        object.__setattr__(session, "notes", model.notes)
        object.__setattr__(session, "created_at", model.created_at)
        object.__setattr__(session, "updated_at", model.updated_at)
        return session

    @staticmethod
    def update_model(model: SessionModel, entity: Session) -> SessionModel:
        """Atualiza model existente com dados da entidade."""
        model.user_id = str(entity.user_id)
        model.patient_id = str(entity.patient_id)
        model.date_time = entity.date_time
        model.duration_minutes = entity.duration_minutes
        model.price = entity.price
        model.status = entity.status.value
        model.notes = entity.notes
        model.updated_at = entity.updated_at
        return model
