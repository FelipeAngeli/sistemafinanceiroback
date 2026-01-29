"""Use Case: Login de Usuário.

Responsável por autenticar um usuário e gerar token JWT.
"""

from dataclasses import dataclass

from app.core.auth.jwt_handler import create_access_token
from app.core.auth.password import verify_password
from app.domain.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class LoginUserInput:
    """Dados de entrada para login."""

    email: str
    password: str


@dataclass(frozen=True)
class LoginUserOutput:
    """Dados de saída após login."""

    access_token: str
    token_type: str = "bearer"
    user_id: str = ""
    user_email: str = ""
    user_name: str = ""


class LoginUserUseCase:
    """Caso de uso para fazer login de usuário.

    Fluxo:
        1. Busca usuário por email
        2. Verifica se usuário existe e está ativo
        3. Verifica senha
        4. Gera token JWT
        5. Retorna token e dados do usuário
    """

    def __init__(self, user_repository: UserRepository) -> None:
        self._repository = user_repository

    async def execute(self, input_data: LoginUserInput) -> LoginUserOutput:
        """Executa o login do usuário."""
        from app.core.exceptions import ValidationError

        # Buscar usuário por email
        user = await self._repository.get_by_email(input_data.email)
        if not user:
            raise ValidationError("Email ou senha inválidos.")

        # Verificar se usuário está ativo
        if not user.is_active():
            raise ValidationError("Usuário inativo.")

        # Verificar senha
        if not verify_password(input_data.password, user.password_hash):
            raise ValidationError("Email ou senha inválidos.")

        # Gerar token JWT
        access_token = create_access_token(data={"sub": str(user.id)})

        # Retornar output
        return LoginUserOutput(
            access_token=access_token,
            token_type="bearer",
            user_id=str(user.id),
            user_email=user.email,
            user_name=user.name,
        )
