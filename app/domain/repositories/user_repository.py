"""
Interface do repositório de usuários.

Define contrato que implementações concretas devem seguir.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.user import User


class UserRepository(ABC):
    """Interface abstrata para persistência de usuários."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Persiste um novo usuário.

        Args:
            user: Entidade User a ser persistida.

        Returns:
            User persistido (com ID gerado se aplicável).
        """
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Busca usuário por ID.

        Args:
            user_id: UUID do usuário.

        Returns:
            User se encontrado, None caso contrário.
        """
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email.

        Args:
            email: Email do usuário.

        Returns:
            User se encontrado, None caso contrário.
        """
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        """Atualiza um usuário existente.

        Args:
            user: Entidade User com dados atualizados.

        Returns:
            User atualizado.
        """
        ...
