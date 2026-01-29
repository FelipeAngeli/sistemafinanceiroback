"""Testes de API para endpoints de Sessões."""

from datetime import datetime
from decimal import Decimal

import pytest
from httpx import AsyncClient


class TestSessionsAPI:
    """Testes para /sessions endpoints."""

    @pytest.fixture
    async def patient_id(self, client: AsyncClient, auth_headers: dict) -> str:
        """Cria paciente e retorna ID."""
        response = await client.post(
            "/patients",
            json={"name": "Paciente Teste"},
            headers=auth_headers,
        )
        return response.json()["id"]

    @pytest.mark.asyncio
    async def test_create_session_success(self, client: AsyncClient, patient_id: str, auth_headers: dict):
        """POST /sessions - deve criar sessão."""
        response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
                "duration_minutes": 50,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["patient_id"] == patient_id
        assert data["status"] == "agendada"
        assert Decimal(data["price"]) == Decimal("200.00")

    @pytest.mark.asyncio
    async def test_create_session_patient_not_found(self, client: AsyncClient, auth_headers: dict):
        """POST /sessions - deve retornar 404 se paciente não existe."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.post(
            "/sessions",
            json={
                "patient_id": fake_id,
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
            },
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_session_status_realizada(
        self, client: AsyncClient, patient_id: str, auth_headers: dict
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
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        # Realizar
        response = await client.patch(
            f"/sessions/{session_id}/status",
            json={"new_status": "realizada"},
            headers=auth_headers,
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
        self, client: AsyncClient, patient_id: str, auth_headers: dict
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
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        # Cancelar
        response = await client.patch(
            f"/sessions/{session_id}/status",
            json={"new_status": "cancelada"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["new_status"] == "cancelada"
        assert data["financial_entry_created"] is False
        assert data["financial_entry_id"] is None

    @pytest.mark.asyncio
    async def test_update_session_not_found(self, client: AsyncClient, auth_headers: dict):
        """PATCH /sessions/{id}/status - deve retornar 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(
            f"/sessions/{fake_id}/status",
            json={"new_status": "realizada"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_session_business_rule_error(
        self, client: AsyncClient, patient_id: str, auth_headers: dict
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
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        # Cancelar
        await client.patch(
            f"/sessions/{session_id}/status",
            json={"new_status": "cancelada"},
            headers=auth_headers,
        )

        # Tentar realizar sessão já cancelada (deve dar erro)
        response = await client.patch(
            f"/sessions/{session_id}/status",
            json={"new_status": "realizada"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_session_validation_error(self, client: AsyncClient, patient_id: str, auth_headers: dict):
        """POST /sessions - erro de validação (preço negativo)."""
        response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": "2024-12-15T14:00:00",
                "price": -100.00,  # Preço negativo inválido
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    # ============================================================
    # Testes para GET /sessions/{id}
    # ============================================================

    @pytest.mark.asyncio
    async def test_get_session_by_id_success(self, client: AsyncClient, patient_id: str, auth_headers: dict):
        """GET /sessions/{id} - deve retornar sessão existente corretamente."""
        # Criar sessão
        create_response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": "2024-01-15T14:30:00",
                "price": 150.00,
                "duration_minutes": 50,
                "notes": "Observações da sessão",
            },
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        # Buscar sessão
        response = await client.get(f"/sessions/{session_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Validar campos obrigatórios
        assert data["id"] == session_id
        assert data["patient_id"] == patient_id
        assert data["status"] == "agendada"
        assert Decimal(str(data["price"])) == Decimal("150.00")
        assert data["duration_minutes"] == 50
        assert data["notes"] == "Observações da sessão"

        # Validar formato ISO 8601 do date_time
        datetime.fromisoformat(data["date_time"].replace("Z", "+00:00"))

    @pytest.mark.asyncio
    async def test_get_session_by_id_with_null_notes(self, client: AsyncClient, patient_id: str, auth_headers: dict):
        """GET /sessions/{id} - deve retornar sessão com notes null."""
        # Criar sessão sem notes
        create_response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": "2024-01-15T14:30:00",
                "price": 150.00,
            },
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        # Buscar sessão
        response = await client.get(f"/sessions/{session_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["notes"] is None

    @pytest.mark.asyncio
    async def test_get_session_by_id_not_found(self, client: AsyncClient, auth_headers: dict):
        """GET /sessions/{id} - deve retornar 404 para sessão inexistente."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/sessions/{fake_id}", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_get_session_by_id_invalid_uuid(self, client: AsyncClient, auth_headers: dict):
        """GET /sessions/{id} - deve retornar 422 para ID inválido (não UUID)."""
        invalid_id = "not-a-uuid"
        response = await client.get(f"/sessions/{invalid_id}", headers=auth_headers)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_session_by_id_all_statuses(self, client: AsyncClient, patient_id: str, auth_headers: dict):
        """GET /sessions/{id} - deve retornar sessão com diferentes status."""
        statuses = ["agendada", "realizada", "cancelada"]

        for status in statuses:
            # Criar sessão
            create_response = await client.post(
                "/sessions",
                json={
                    "patient_id": patient_id,
                    "date_time": "2024-01-15T14:30:00",
                    "price": 150.00,
                },
                headers=auth_headers,
            )
            session_id = create_response.json()["id"]

            # Atualizar status se necessário
            if status != "agendada":
                await client.patch(
                    f"/sessions/{session_id}/status",
                    json={"new_status": status},
                    headers=auth_headers,
                )

            # Buscar sessão
            response = await client.get(f"/sessions/{session_id}", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == status

    @pytest.mark.asyncio
    async def test_get_session_by_id_data_types(self, client: AsyncClient, patient_id: str, auth_headers: dict):
        """GET /sessions/{id} - deve retornar tipos de dados corretos."""
        # Criar sessão
        create_response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": "2024-01-15T14:30:00",
                "price": 150.50,
                "duration_minutes": 60,
                "notes": "Teste",
            },
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        # Buscar sessão
        response = await client.get(f"/sessions/{session_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Validar tipos
        assert isinstance(data["id"], str)  # UUID serializado como string
        assert isinstance(data["patient_id"], str)  # UUID serializado como string
        assert isinstance(data["date_time"], str)  # datetime serializado como ISO string
        assert isinstance(data["price"], (int, float, str))  # Decimal pode ser serializado como número ou string
        assert isinstance(data["duration_minutes"], int)
        assert isinstance(data["status"], str)
        assert isinstance(data["notes"], str) or data["notes"] is None

        # Validar valores específicos
        assert Decimal(str(data["price"])) == Decimal("150.50")
        assert data["duration_minutes"] == 60
        assert data["status"] in ["agendada", "realizada", "cancelada", "faltou"]

    @pytest.mark.asyncio
    async def test_sessions_require_authentication(self, client: AsyncClient):
        """Testa que endpoints de sessões requerem autenticação."""
        # Tentar criar sessão sem token
        response = await client.post(
            "/sessions",
            json={
                "patient_id": "00000000-0000-0000-0000-000000000000",
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
            },
        )
        assert response.status_code == 401

        # Tentar listar sessões sem token
        response = await client.get("/sessions")
        assert response.status_code == 401

        # Tentar buscar sessão sem token
        response = await client.get("/sessions/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 401
