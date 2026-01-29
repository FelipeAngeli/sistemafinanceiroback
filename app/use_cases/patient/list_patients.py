"""
Use Case: Listar Pacientes.

Responsável por listar todos os pacientes cadastrados.
"""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from app.domain.repositories.patient_repository import PatientRepository


@dataclass(frozen=True)
class ListPatientsInput:
    """Dados de entrada para listagem de pacientes."""

    user_id: UUID
    active_only: bool = True


@dataclass(frozen=True)
class PatientSummary:
    """Resumo de um paciente para listagem."""

    id: UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    observation: Optional[str]
    active: bool


@dataclass
class ListPatientsOutput:
    """Dados de saída da listagem de pacientes."""

    patients: List[PatientSummary]
    total: int


class ListPatientsUseCase:
    """Caso de uso para listar pacientes.

    Fluxo:
        1. Busca pacientes no repositório
        2. Converte para lista de resumos
        3. Retorna output com lista e total
    """

    def __init__(self, patient_repository: PatientRepository) -> None:
        self._repository = patient_repository

    async def execute(self, input_data: ListPatientsInput) -> ListPatientsOutput:
        """Executa a listagem de pacientes."""
        patients = await self._repository.list_all(
            user_id=input_data.user_id,
            active_only=input_data.active_only,
        )

        summaries = [
            PatientSummary(
                id=p.id,
                name=p.name,
                email=p.email,
                phone=p.phone,
                observation=p.observation,
                active=p.active,
            )
            for p in patients
        ]

        return ListPatientsOutput(
            patients=summaries,
            total=len(summaries),
        )
