"""Testes unitários para use cases de autenticação."""

import pytest
from uuid import UUID

from app.core.auth.password import hash_password, verify_password
from app.core.exceptions import ValidationError
from app.domain.entities.user import User
from app.use_cases.auth.register_user import RegisterUserInput, RegisterUserUseCase
from app.use_cases.auth.login_user import LoginUserInput, LoginUserUseCase
from tests.fakes.fake_repositories import FakeUserRepository


class TestRegisterUserUseCase:
    """Testes para RegisterUserUseCase."""

    @pytest.fixture
    def user_repository(self):
        """Repositório fake de usuários."""
        return FakeUserRepository()

    @pytest.fixture
    def use_case(self, user_repository):
        """Use case de registro."""
        return RegisterUserUseCase(user_repository=user_repository)

    @pytest.mark.asyncio
    async def test_register_user_success(self, use_case):
        """Deve registrar usuário com sucesso."""
        input_data = RegisterUserInput(
            email="teste@example.com",
            password="senha123",
            name="Usuário Teste",
        )

        output = await use_case.execute(input_data)

        assert output.email == "teste@example.com"
        assert output.name == "Usuário Teste"
        assert isinstance(output.id, UUID)

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, use_case):
        """Deve retornar erro se email já existe."""
        # Registrar primeiro usuário
        await use_case.execute(
            RegisterUserInput(
                email="duplicado@example.com",
                password="senha123",
                name="Primeiro",
            )
        )

        # Tentar registrar segundo com mesmo email
        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(
                RegisterUserInput(
                    email="duplicado@example.com",
                    password="senha456",
                    name="Segundo",
                )
            )

        assert "já está em uso" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_register_user_validates_email(self, use_case):
        """Deve validar formato de email."""
        with pytest.raises(ValidationError):
            await use_case.execute(
                RegisterUserInput(
                    email="email-invalido",
                    password="senha123",
                    name="Teste",
                )
            )

    @pytest.mark.asyncio
    async def test_register_user_validates_name(self, use_case):
        """Deve validar nome."""
        with pytest.raises(ValidationError):
            await use_case.execute(
                RegisterUserInput(
                    email="teste@example.com",
                    password="senha123",
                    name="A",  # Muito curto
                )
            )


class TestLoginUserUseCase:
    """Testes para LoginUserUseCase."""

    @pytest.fixture
    def user_repository(self):
        """Repositório fake de usuários."""
        return FakeUserRepository()

    @pytest.fixture
    async def registered_user(self, user_repository):
        """Usuário já registrado."""
        register_use_case = RegisterUserUseCase(user_repository=user_repository)
        return await register_use_case.execute(
            RegisterUserInput(
                email="login@example.com",
                password="senha123",
                name="Usuário Login",
            )
        )

    @pytest.fixture
    def use_case(self, user_repository):
        """Use case de login."""
        return LoginUserUseCase(user_repository=user_repository)

    @pytest.mark.asyncio
    async def test_login_success(self, use_case, registered_user):
        """Deve fazer login com sucesso."""
        input_data = LoginUserInput(
            email="login@example.com",
            password="senha123",
        )

        output = await use_case.execute(input_data)

        assert output.access_token is not None
        assert output.token_type == "bearer"
        assert output.user_email == "login@example.com"
        assert output.user_name == "Usuário Login"
        assert output.user_id == str(registered_user.id)

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, use_case):
        """Deve retornar erro se email não existe."""
        input_data = LoginUserInput(
            email="naoexiste@example.com",
            password="senha123",
        )

        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(input_data)

        assert "inválidos" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, use_case, registered_user):
        """Deve retornar erro se senha incorreta."""
        input_data = LoginUserInput(
            email="login@example.com",
            password="senhaerrada",
        )

        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(input_data)

        assert "inválidos" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, user_repository, use_case):
        """Deve retornar erro se usuário inativo."""
        # Criar usuário inativo diretamente
        user = User(
            email="inativo@example.com",
            password_hash=hash_password("senha123"),
            name="Usuário Inativo",
        )
        user.deactivate()
        await user_repository.create(user)

        input_data = LoginUserInput(
            email="inativo@example.com",
            password="senha123",
        )

        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(input_data)

        assert "inativo" in str(exc_info.value).lower()


class TestPasswordHashing:
    """Testes para funções de hash de senha."""

    def test_hash_password(self):
        """Deve gerar hash de senha."""
        password = "senha123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # Bcrypt hash format

    def test_verify_password_correct(self):
        """Deve verificar senha correta."""
        password = "senha123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Deve rejeitar senha incorreta."""
        password = "senha123"
        hashed = hash_password(password)

        assert verify_password("senhaerrada", hashed) is False

    def test_hash_password_different_each_time(self):
        """Hash deve ser diferente a cada vez (salt)."""
        password = "senha123"
        hashed1 = hash_password(password)
        hashed2 = hash_password(password)

        # Hashes devem ser diferentes devido ao salt
        assert hashed1 != hashed2
        # Mas ambos devem verificar a mesma senha
        assert verify_password(password, hashed1) is True
        assert verify_password(password, hashed2) is True
