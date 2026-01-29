"""Mapper para converter entre User (entidade) e UserModel (ORM)."""

from uuid import UUID

from app.domain.entities.user import User
from app.infra.db.models.user_model import UserModel


class UserMapper:
    """Converte entre User e UserModel."""

    @staticmethod
    def to_model(entity: User) -> UserModel:
        """Converte entidade de domínio para model ORM.

        Args:
            entity: Entidade User do domínio.

        Returns:
            UserModel para persistência.
        """
        return UserModel(
            id=str(entity.id),
            email=entity.email,
            password_hash=entity.password_hash,
            name=entity.name,
            active=entity.active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(model: UserModel) -> User:
        """Converte model ORM para entidade de domínio.

        Args:
            model: UserModel do banco.

        Returns:
            Entidade User do domínio.

        Note:
            Usamos object.__setattr__ para evitar validações
            do __post_init__ em dados já validados do banco.
        """
        user = object.__new__(User)
        object.__setattr__(user, "id", UUID(model.id))
        object.__setattr__(user, "email", model.email)
        object.__setattr__(user, "password_hash", model.password_hash)
        object.__setattr__(user, "name", model.name)
        object.__setattr__(user, "active", model.active)
        object.__setattr__(user, "created_at", model.created_at)
        object.__setattr__(user, "updated_at", model.updated_at)
        return user

    @staticmethod
    def update_model(model: UserModel, entity: User) -> UserModel:
        """Atualiza um model existente com dados da entidade.

        Args:
            model: UserModel existente.
            entity: Entidade User com dados atualizados.

        Returns:
            UserModel atualizado.
        """
        model.email = entity.email
        model.password_hash = entity.password_hash
        model.name = entity.name
        model.active = entity.active
        model.updated_at = entity.updated_at
        return model
