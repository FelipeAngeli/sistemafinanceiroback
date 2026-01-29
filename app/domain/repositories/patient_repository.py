"""
Interface do repositório de pacientes.

Define contrato que implementações concretas devem seguir.
Não contém nenhuma dependência de banco de dados ou ORM.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.patient import Patient, PatientStats


class PatientRepository(ABC):
    """Interface abstrata para persistência de pacientes.

    Esta interface será implementada na camada de infraestrutura
    com a tecnologia de banco de dados escolhida (PostgreSQL, DynamoDB, etc).
    """

    @abstractmethod
    async def get_stats(self, user_id: UUID) -> PatientStats:
        """Retorna estatísticas gerais dos pacientes (total, ativos, inativos) do usuário.
        
        Args:
            user_id: UUID do usuário.
        """
        ...

    @abstractmethod
    async def create(self, patient: Patient) -> Patient:
        """Persiste um novo paciente.

        Args:
            patient: Entidade Patient a ser persistida.

        Returns:
            Patient persistido (com ID gerado se aplicável).
        """
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID, patient_id: UUID) -> Optional[Patient]:
        """Busca paciente por ID.

        Args:
            user_id: UUID do usuário (dono do paciente).
            patient_id: UUID do paciente.

        Returns:
            Patient se encontrado e pertencer ao usuário, None caso contrário.
        """
        ...

    @abstractmethod
    async def list_all(self, user_id: UUID, active_only: bool = True) -> List[Patient]:
        """Lista todos os pacientes do usuário.

        Args:
            user_id: UUID do usuário.
            active_only: Se True, retorna apenas pacientes ativos.

        Returns:
            Lista de pacientes do usuário.
        """
        ...

    @abstractmethod
    async def update(self, patient: Patient) -> Patient:
        """Atualiza um paciente existente.

        Args:
            patient: Entidade Patient com dados atualizados.

        Returns:
            Patient atualizado.
        """
        ...

    @abstractmethod
    async def delete(self, user_id: UUID, patient_id: UUID) -> bool:
        """Remove um paciente (hard delete).

        Args:
            user_id: UUID do usuário (dono do paciente).
            patient_id: UUID do paciente a ser removido.

        Returns:
            True se removido com sucesso, False se não encontrado ou não pertencer ao usuário.
        """
        ...
