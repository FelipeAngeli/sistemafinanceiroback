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
    notes: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    active: bool = True

    def __post_init__(self) -> None:
        """Validações após inicialização."""
        self._validate_name()
        self._validate_email()

    def _validate_name(self) -> None:
        """Valida o nome do paciente."""
        if not self.name or not self.name.strip():
            raise ValidationError("Nome do paciente é obrigatório.")
        self.name = self.name.strip()
        if len(self.name) < 2:
            raise ValidationError("Nome deve ter pelo menos 2 caracteres.")

    def _validate_email(self) -> None:
        """Valida formato básico do email."""
        if self.email is not None:
            self.email = self.email.strip()
            if self.email and "@" not in self.email:
                raise ValidationError("Email inválido.")

    def deactivate(self) -> None:
        """Desativa o paciente (soft delete)."""
        self.active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Reativa o paciente."""
        self.active = True
        self.updated_at = datetime.utcnow()

    def update(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        notes: Optional[str] = None,
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
        if notes is not None:
            self.notes = notes
        self.updated_at = datetime.utcnow()
