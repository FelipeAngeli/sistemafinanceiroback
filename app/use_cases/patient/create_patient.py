"""Use Case: Criar Paciente.

Responsável por criar um novo paciente no sistema.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.domain.entities.patient import Patient
from app.domain.repositories.patient_repository import PatientRepository


@dataclass(frozen=True)
class CreatePatientInput:
    """Dados de entrada para criação de paciente."""

    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    observation: Optional[str] = None


@dataclass(frozen=True)
class CreatePatientOutput:
    """Dados de saída após criação de paciente."""

    id: UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    observation: Optional[str]
    active: bool


class CreatePatientUseCase:
    """Caso de uso para criar um novo paciente.

    Fluxo:
        1. Recebe dados do paciente
        2. Cria entidade Patient (validações são feitas na entidade)
        3. Persiste via repositório
        4. Retorna output com dados do paciente criado
    """

    def __init__(self, patient_repository: PatientRepository) -> None:
        self._repository = patient_repository

    async def execute(self, input_data: CreatePatientInput) -> CreatePatientOutput:
        """Executa a criação do paciente."""
        # Criar entidade (validações ocorrem no __post_init__)
        patient = Patient(
            name=input_data.name,
            email=input_data.email,
            phone=input_data.phone,
            observation=input_data.observation,
        )

        # Persistir
        saved_patient = await self._repository.create(patient)

        # Retornar output
        return CreatePatientOutput(
            id=saved_patient.id,
            name=saved_patient.name,
            email=saved_patient.email,
            phone=saved_patient.phone,
            observation=saved_patient.observation,
            active=saved_patient.active,
        )
