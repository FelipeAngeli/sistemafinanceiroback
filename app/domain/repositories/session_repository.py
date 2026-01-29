"""Interface do repositório de sessões.

Define contrato que implementações concretas devem seguir.
Não contém nenhuma dependência de banco de dados ou ORM.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from uuid import UUID

from app.domain.entities.session import Session


class SessionRepository(ABC):
    """Interface abstrata para persistência de sessões.

    Esta interface será implementada na camada de infraestrutura
    com a tecnologia de banco de dados escolhida.
    """

    @abstractmethod
    async def create(self, session: Session) -> Session:
        """Persiste uma nova sessão.

        Args:
            session: Entidade Session a ser persistida.

        Returns:
            Session persistida.
        """
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID, session_id: UUID) -> Optional[Session]:
        """Busca sessão por ID, validando que pertence ao usuário.

        Args:
            user_id: UUID do usuário (dono da sessão).
            session_id: UUID da sessão.

        Returns:
            Session se encontrada e pertencer ao usuário, None caso contrário.
        """
        ...

    @abstractmethod
    async def list_by_patient(self, user_id: UUID, patient_id: UUID) -> List[Session]:
        """Lista todas as sessões de um paciente do usuário.

        Args:
            user_id: UUID do usuário (dono das sessões).
            patient_id: UUID do paciente.

        Returns:
            Lista de sessões do paciente do usuário, ordenadas por data.
        """
        ...

    @abstractmethod
    async def list_recent(self, user_id: UUID, limit: int = 10) -> List[Session]:
        """Lista as sessões mais recentes do usuário.

        Args:
            user_id: UUID do usuário.
            limit: Número máximo de sessões a retornar.

        Returns:
            Lista das sessões mais recentes do usuário, ordenadas por data descendente.
        """
        ...

    @abstractmethod
    async def update(self, session: Session) -> Session:
        """Atualiza uma sessão existente.

        Args:
            session: Entidade Session com dados atualizados.

        Returns:
            Session atualizada.
        """
        ...

    @abstractmethod
    async def list_all(
        self,
        user_id: UUID,
        patient_id: Optional[UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
    ) -> List[Session]:
        """Lista sessões do usuário com filtros opcionais.

        Args:
            user_id: UUID do usuário (obrigatório).
            patient_id: Filtrar por paciente.
            status: Filtrar por status.
            start_date: Data inicial.
            end_date: Data final.
            limit: Limite de resultados.

        Returns:
            Lista de sessões do usuário filtradas.
        """
        ...
