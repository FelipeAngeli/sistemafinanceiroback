"""Testes de API para endpoints Financeiros."""

from decimal import Decimal

import pytest
from httpx import AsyncClient


class TestFinancialAPI:
    """Testes para /financial endpoints."""

    @pytest.fixture
    async def setup_paid_session(self, client: AsyncClient) -> dict:
        """Cria paciente, sessão e conclui (gera lançamento)."""
        # Criar paciente
        patient_response = await client.post(
            "/patients",
            json={"name": "Paciente Financeiro"},
        )
        patient_id = patient_response.json()["id"]

        # Criar sessão
        session_response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
            },
        )
        session_id = session_response.json()["id"]

        # Concluir sessão
        status_response = await client.patch(
            f"/sessions/{session_id}/status",
            json={"new_status": "concluida"},
        )

        return {
            "patient_id": patient_id,
            "session_id": session_id,
            "financial_entry_id": status_response.json()["financial_entry_id"],
        }

    @pytest.mark.asyncio
    async def test_list_financial_entries(
        self, client: AsyncClient, setup_paid_session: dict
    ):
        """GET /financial/entries - deve listar lançamentos."""
        response = await client.get(
            "/financial/entries",
            params={
                "start_date": "2024-12-01",
                "end_date": "2024-12-31",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        assert "total_entries" in data
        assert "total_amount" in data
        assert "total_pending" in data
        assert "total_paid" in data
        assert data["total_entries"] >= 1

    @pytest.mark.asyncio
    async def test_list_financial_entries_filter_pending(
        self, client: AsyncClient, setup_paid_session: dict
    ):
        """GET /financial/entries - deve filtrar por status pendente."""
        response = await client.get(
            "/financial/entries",
            params={
                "start_date": "2024-12-01",
                "end_date": "2024-12-31",
                "status": "pendente",
            },
        )

        assert response.status_code == 200
        data = response.json()
        # Todos os lançamentos devem ser pendentes
        for entry in data["entries"]:
            assert entry["status"] == "pendente"

    @pytest.mark.asyncio
    async def test_financial_report_empty_period(self, client: AsyncClient):
        """GET /financial/entries - período sem lançamentos."""
        response = await client.get(
            "/financial/entries",
            params={
                "start_date": "2020-01-01",
                "end_date": "2020-01-31",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_entries"] == 0
        assert Decimal(data["total_amount"]) == Decimal("0")

    @pytest.mark.asyncio
    async def test_financial_entries_requires_dates(self, client: AsyncClient):
        """GET /financial/entries - deve exigir datas."""
        response = await client.get("/financial/entries")

        assert response.status_code == 422  # Validation error
