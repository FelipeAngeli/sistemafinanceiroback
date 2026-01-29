"""Interface do repositório de lançamentos financeiros.

Define contrato que implementações concretas devem seguir.
Não contém nenhuma dependência de banco de dados ou ORM.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from uuid import UUID

from app.domain.entities.financial_entry import EntryStatus, FinancialEntry


class FinancialEntryRepository(ABC):
    """Interface abstrata para persistência de lançamentos financeiros.

    Esta interface será implementada na camada de infraestrutura
    com a tecnologia de banco de dados escolhida.
    """

    @abstractmethod
    async def create(self, entry: FinancialEntry) -> FinancialEntry:
        """Persiste um novo lançamento financeiro.

        Args:
            entry: Entidade FinancialEntry a ser persistida.

        Returns:
            FinancialEntry persistido.
        """
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID, entry_id: UUID) -> Optional[FinancialEntry]:
        """Busca lançamento por ID, validando que pertence ao usuário.

        Args:
            user_id: UUID do usuário (dono do lançamento).
            entry_id: UUID do lançamento.

        Returns:
            FinancialEntry se encontrado e pertencer ao usuário, None caso contrário.
        """
        ...

    @abstractmethod
    async def list_by_period(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
        status_filter: Optional[List[EntryStatus]] = None,
    ) -> List[FinancialEntry]:
        """Lista lançamentos do usuário em um período, opcionalmente filtrados por status.

        Args:
            user_id: UUID do usuário (obrigatório).
            start_date: Data inicial do período.
            end_date: Data final do período.
            status_filter: Lista de status para filtrar (None = todos).

        Returns:
            Lista de lançamentos do usuário no período.
        """
        ...

    @abstractmethod
    async def list_pending(self, user_id: UUID) -> List[FinancialEntry]:
        """Lista todos os lançamentos pendentes do usuário.

        Args:
            user_id: UUID do usuário.

        Returns:
            Lista de lançamentos do usuário com status PENDENTE.
        """
        ...

    @abstractmethod
    async def update(self, entry: FinancialEntry) -> FinancialEntry:
        """Atualiza um lançamento existente.

        Args:
            entry: Entidade FinancialEntry com dados atualizados.

        Returns:
            FinancialEntry atualizado.
        """
        ...
