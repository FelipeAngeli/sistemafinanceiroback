"""Implementação SQLAlchemy do repositório de usuários."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infra.db.mappers.user_mapper import UserMapper
from app.infra.db.models.user_model import UserModel


class SqlAlchemyUserRepository(UserRepository):
    """Implementação SQLAlchemy do repositório de usuários."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user: User) -> User:
        """Persiste um novo usuário."""
        try:
            model = UserMapper.to_model(user)
            self._session.add(model)
            await self._session.commit()
            await self._session.refresh(model)
            return UserMapper.to_entity(model)
        except Exception as e:
            await self._session.rollback()
            raise

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Busca usuário por ID."""
        stmt = select(UserModel).where(UserModel.id == str(user_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email."""
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None

    async def update(self, user: User) -> User:
        """Atualiza um usuário existente."""
        from app.core.exceptions import EntityNotFoundError
        
        stmt = select(UserModel).where(UserModel.id == str(user.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("Usuário", str(user.id))
        UserMapper.update_model(model, user)
        await self._session.commit()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)
