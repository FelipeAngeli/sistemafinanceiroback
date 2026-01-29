"""Entidade User (Usuário).

Representa um usuário do sistema.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.core.exceptions import ValidationError


@dataclass
class User:
    """Entidade Usuário."""

    email: str
    password_hash: str
    name: str
    id: UUID = field(default_factory=uuid4)
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validações após inicialização."""
        self._validate_email()
        self._validate_name()
        self._validate_password_hash()

    def _validate_email(self) -> None:
        """Valida o email do usuário."""
        if not self.email or not self.email.strip():
            raise ValidationError("Email é obrigatório.")
        self.email = self.email.strip().lower()
        if "@" not in self.email:
            raise ValidationError("Email inválido.")
        if len(self.email) > 255:
            raise ValidationError("Email não pode ter mais de 255 caracteres.")
        parts = self.email.split("@")
        if len(parts) != 2 or "." not in parts[1]:
            raise ValidationError("Email inválido.")

    def _validate_name(self) -> None:
        """Valida o nome do usuário."""
        if not self.name or not self.name.strip():
            raise ValidationError("Nome é obrigatório.")
        self.name = self.name.strip()
        if len(self.name) < 2:
            raise ValidationError("Nome deve ter pelo menos 2 caracteres.")
        if len(self.name) > 255:
            raise ValidationError("Nome não pode ter mais de 255 caracteres.")

    def _validate_password_hash(self) -> None:
        """Valida que password_hash não está vazio."""
        if not self.password_hash or not self.password_hash.strip():
            raise ValidationError("Password hash é obrigatório.")

    def deactivate(self) -> None:
        """Desativa o usuário."""
        self.active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """Reativa o usuário."""
        self.active = True
        self.updated_at = datetime.now(UTC)

    def is_active(self) -> bool:
        """Verifica se o usuário está ativo."""
        return self.active
