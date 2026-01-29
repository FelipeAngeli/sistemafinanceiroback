"""Use Case: Registrar Usuário.

Responsável por criar um novo usuário no sistema.
"""

from dataclasses import dataclass
from uuid import UUID

from app.core.auth.password import hash_password
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class RegisterUserInput:
    """Dados de entrada para registro de usuário."""

    email: str
    password: str
    name: str


@dataclass(frozen=True)
class RegisterUserOutput:
    """Dados de saída após registro de usuário."""

    id: UUID
    email: str
    name: str


class RegisterUserUseCase:
    """Caso de uso para registrar um novo usuário.

    Fluxo:
        1. Verifica se email já existe
        2. Gera hash da senha
        3. Cria entidade User
        4. Persiste via repositório
        5. Retorna dados do usuário (sem senha)
    """

    def __init__(self, user_repository: UserRepository) -> None:
        self._repository = user_repository

    async def execute(self, input_data: RegisterUserInput) -> RegisterUserOutput:
        """Executa o registro do usuário."""
        # Verificar se email já existe
        existing_user = await self._repository.get_by_email(input_data.email)
        if existing_user:
            from app.core.exceptions import ValidationError
            raise ValidationError("Email já está em uso.")

        # Gerar hash da senha
        password_hash = hash_password(input_data.password)

        # Criar entidade (validações ocorrem no __post_init__)
        user = User(
            email=input_data.email,
            password_hash=password_hash,
            name=input_data.name,
        )

        # Persistir
        saved_user = await self._repository.create(user)

        # Retornar output (sem senha)
        return RegisterUserOutput(
            id=saved_user.id,
            email=saved_user.email,
            name=saved_user.name,
        )
