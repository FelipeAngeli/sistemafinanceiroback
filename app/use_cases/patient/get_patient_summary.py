"""Use Case: Obter Resumo de Pacientes.

Responsável por obter estatísticas otimizadas sobre os pacientes.
"""

from dataclasses import dataclass
from uuid import UUID

from app.domain.repositories.patient_repository import PatientRepository


@dataclass(frozen=True)
class GetPatientSummaryInput:
    """Dados de entrada para resumo de pacientes."""

    user_id: UUID


@dataclass(frozen=True)
class PatientSummaryOutput:
    """Dados de saída do resumo de pacientes."""

    total: int
    active: int
    inactive: int
    percentage_active: float


class GetPatientSummaryUseCase:
    """Caso de uso para obter resumo de pacientes.
    
    Fluxo:
        1. Busca estatísticas no repositório (query otimizada)
        2. Calcula porcentagem de ativos
        3. Retorna output
    """

    def __init__(self, patient_repository: PatientRepository) -> None:
        self._repository = patient_repository

    async def execute(self, input_data: GetPatientSummaryInput) -> PatientSummaryOutput:
        """Executa a busca de estatísticas."""
        stats = await self._repository.get_stats(user_id=input_data.user_id)
        
        percentage = 0.0
        if stats.total > 0:
            percentage = (stats.active / stats.total) * 100
            
        return PatientSummaryOutput(
            total=stats.total,
            active=stats.active,
            inactive=stats.inactive,
            percentage_active=round(percentage, 2),
        )
