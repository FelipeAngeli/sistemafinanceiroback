"""Mapper entre Patient (domínio) e PatientModel (ORM)."""

from uuid import UUID

from app.domain.entities.patient import Patient
from app.infra.db.models.patient_model import PatientModel


class PatientMapper:
    """Converte entre Patient e PatientModel."""

    @staticmethod
    def to_model(entity: Patient) -> PatientModel:
        """Converte entidade de domínio para model ORM.

        Args:
            entity: Entidade Patient do domínio.

        Returns:
            PatientModel para persistência.
        """
        return PatientModel(
            id=str(entity.id),
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            observation=entity.observation,
            active=entity.active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(model: PatientModel) -> Patient:
        """Converte model ORM para entidade de domínio.

        Args:
            model: PatientModel do banco.

        Returns:
            Entidade Patient do domínio.

        Note:
            Usamos object.__setattr__ para evitar validações
            do __post_init__ em dados já validados do banco.
        """
        patient = object.__new__(Patient)
        object.__setattr__(patient, "id", UUID(model.id))
        object.__setattr__(patient, "name", model.name)
        object.__setattr__(patient, "email", model.email)
        object.__setattr__(patient, "phone", model.phone)
        object.__setattr__(patient, "observation", model.observation)
        object.__setattr__(patient, "active", model.active)
        object.__setattr__(patient, "created_at", model.created_at)
        object.__setattr__(patient, "updated_at", model.updated_at)
        return patient

    @staticmethod
    def update_model(model: PatientModel, entity: Patient) -> PatientModel:
        """Atualiza model existente com dados da entidade.

        Args:
            model: PatientModel existente.
            entity: Entidade Patient com dados atualizados.

        Returns:
            PatientModel atualizado.
        """
        model.name = entity.name
        model.email = entity.email
        model.phone = entity.phone
        model.observation = entity.observation
        model.active = entity.active
        model.updated_at = entity.updated_at
        return model
