"""
Controller HTTP para Pacientes.

Stub para futura implementação com FastAPI.
"""

from typing import List
from uuid import UUID


class PatientController:
    """Controller REST para pacientes."""

    async def create(self, data: dict) -> dict:
        """POST /patients - Cria um novo paciente."""
        pass

    async def get(self, patient_id: UUID) -> dict:
        """GET /patients/{id} - Busca paciente por ID."""
        pass

    async def list(self) -> List[dict]:
        """GET /patients - Lista todos os pacientes."""
        pass

    async def update(self, patient_id: UUID, data: dict) -> dict:
        """PUT /patients/{id} - Atualiza um paciente."""
        pass

    async def delete(self, patient_id: UUID) -> None:
        """DELETE /patients/{id} - Remove um paciente."""
        pass
