"""Entidade Patient (Paciente).

Representa um paciente atendido pela psicóloga.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from app.core.exceptions import ValidationError


@dataclass
class PatientStats:
    """Estatísticas de pacientes."""
    
    total: int
    active: int
    inactive: int


@dataclass
class Patient:
    """Entidade Paciente."""

    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    observation: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    active: bool = True

    def __post_init__(self) -> None:
        """Validações após inicialização."""
        self._validate_name()
        self._validate_email()
        self._validate_phone()

    def _validate_name(self) -> None:
        """Valida o nome do paciente."""
        if not self.name or not self.name.strip():
            raise ValidationError("Nome do paciente é obrigatório.")
        self.name = self.name.strip()
        if len(self.name) < 2:
            raise ValidationError("Nome deve ter pelo menos 2 caracteres.")
        if len(self.name) > 200:
            raise ValidationError("Nome não pode ter mais de 200 caracteres.")

    def _validate_email(self) -> None:
        """Valida formato básico do email."""
        if self.email is not None:
            self.email = self.email.strip().lower()
            if self.email:
                if "@" not in self.email:
                    raise ValidationError("Email inválido.")
                if len(self.email) > 255:
                    raise ValidationError("Email não pode ter mais de 255 caracteres.")
                # Validação básica: deve ter pelo menos um ponto após o @
                parts = self.email.split("@")
                if len(parts) != 2 or "." not in parts[1]:
                    raise ValidationError("Email inválido.")

    def _validate_phone(self) -> None:
        """Valida formato básico do telefone."""
        if self.phone is not None:
            self.phone = self.phone.strip()
            if self.phone:
                # Remove caracteres não numéricos para validação
                digits_only = "".join(filter(str.isdigit, self.phone))
                if len(digits_only) < 10 or len(digits_only) > 15:
                    raise ValidationError(
                        "Telefone deve ter entre 10 e 15 dígitos numéricos."
                    )

    def deactivate(self) -> None:
        """Desativa o paciente (soft delete)."""
        self.active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Reativa o paciente."""
        self.active = True
        self.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        """Verifica se o paciente está ativo."""
        return self.active

    def has_contact_info(self) -> bool:
        """Verifica se o paciente tem pelo menos um meio de contato (email ou telefone)."""
        return bool(self.email or self.phone)

    def update(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        observation: Optional[str] = None,
    ) -> None:
        """Atualiza dados do paciente."""
        if name is not None:
            self.name = name
            self._validate_name()
        if email is not None:
            self.email = email
            self._validate_email()
        if phone is not None:
            self.phone = phone
            self._validate_phone()
        if observation is not None:
            self.observation = observation
            if len(self.observation) > 1000:
                raise ValidationError("Observação não pode ter mais de 1000 caracteres.")
        self.updated_at = datetime.utcnow()
