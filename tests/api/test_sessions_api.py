"""Testes de API para endpoints de Sessões."""

from datetime import datetime
from decimal import Decimal

import pytest
from httpx import AsyncClient


class TestSessionsAPI:
    """Testes para /sessions endpoints."""

    @pytest.fixture
    async def patient_id(self, client: AsyncClient) -> str:
        """Cria paciente e retorna ID."""
        response = await client.post(
            "/patients",
            json={"name": "Paciente Teste"},
        )
        return response.json()["id"]

    @pytest.mark.asyncio
    async def test_create_session_success(self, client: AsyncClient, patient_id: str):
        """POST /sessions - deve criar sessão."""
        response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
                "duration_minutes": 50,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["patient_id"] == patient_id
        assert data["status"] == "agendada"
        assert Decimal(data["price"]) == Decimal("200.00")

    @pytest.mark.asyncio
    async def test_create_session_patient_not_found(self, client: AsyncClient):
        """POST /sessions - deve retornar 404 se paciente não existe."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.post(
            "/sessions",
            json={
                "patient_id": fake_id,
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
            },
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_session_status_realizada(
        self, client: AsyncClient, patient_id: str
    ):
        """PATCH /sessions/{id}/status - realizar deve criar lançamento."""
        # Criar sessão
        create_response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
            },
        )
        session_id = create_response.json()["id"]

        # Realizar
        response = await client.patch(
            f"/sessions/{session_id}/status",
            json={"new_status": "realizada"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["previous_status"] == "agendada"
        assert data["new_status"] == "realizada"
        assert data["financial_entry_created"] is True
        assert data["financial_entry_id"] is not None
        assert Decimal(data["financial_entry_amount"]) == Decimal("200.00")

    @pytest.mark.asyncio
    async def test_update_session_status_cancelada(
        self, client: AsyncClient, patient_id: str
    ):
        """PATCH /sessions/{id}/status - cancelar NÃO deve criar lançamento."""
        # Criar sessão
        create_response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": "2024-12-20T10:00:00",
                "price": 180.00,
            },
        )
        session_id = create_response.json()["id"]

        # Cancelar
        response = await client.patch(
            f"/sessions/{session_id}/status",
            json={"new_status": "cancelada"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["new_status"] == "cancelada"
        assert data["financial_entry_created"] is False
        assert data["financial_entry_id"] is None

    @pytest.mark.asyncio
    async def test_update_session_not_found(self, client: AsyncClient):
        """PATCH /sessions/{id}/status - deve retornar 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(
            f"/sessions/{fake_id}/status",
            json={"new_status": "realizada"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_session_business_rule_error(
        self, client: AsyncClient, patient_id: str
    ):
        """PATCH /sessions/{id}/status - erro ao realizar sessão já cancelada."""
        # Criar sessão
        create_response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": "2024-12-25T10:00:00",
                "price": 200.00,
            },
        )
        session_id = create_response.json()["id"]

        # Cancelar
        await client.patch(
            f"/sessions/{session_id}/status",
            json={"new_status": "cancelada"},
        )

        # Tentar realizar sessão já cancelada (deve dar erro)
        response = await client.patch(
            f"/sessions/{session_id}/status",
            json={"new_status": "realizada"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_session_validation_error(self, client: AsyncClient, patient_id: str):
        """POST /sessions - erro de validação (preço negativo)."""
        response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": "2024-12-15T14:00:00",
                "price": -100.00,  # Preço negativo inválido
            },
        )

        assert response.status_code == 422
