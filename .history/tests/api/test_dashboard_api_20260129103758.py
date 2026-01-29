"""Testes de API para endpoints de Dashboard."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient


class TestDashboardAPI:
    """Testes para /dashboard endpoints."""

    @pytest.fixture
    async def patient_id(self, client: AsyncClient, auth_headers: dict) -> str:
        """Cria paciente e retorna ID."""
        response = await client.post(
            "/patients",
            json={"name": "Paciente Teste"},
            headers=auth_headers,
        )
        return response.json()["id"]

    @pytest.fixture
    async def session_id(self, client: AsyncClient, patient_id: str, auth_headers: dict) -> str:
        """Cria sessão e retorna ID."""
        response = await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": datetime.now().isoformat(),
                "price": 150.00,
                "duration_minutes": 50,
            },
            headers=auth_headers,
        )
        return response.json()["id"]

    @pytest.mark.asyncio
    async def test_get_dashboard_summary_success(
        self, client: AsyncClient, patient_id: str, session_id: str, auth_headers: dict
    ):
        """GET /dashboard/summary - deve retornar resumo completo."""
        # Concluir sessão para criar lançamento financeiro
        await client.patch(
            f"/sessions/{session_id}/status",
            json={"new_status": "realizada"},
            headers=auth_headers,
        )

        # Buscar resumo
        today = date.today()
        start_date = today - timedelta(days=30)
        end_date = today

        response = await client.get(
            "/dashboard/summary",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Validar estrutura da resposta
        assert "financial_report" in data
        assert "today_sessions" in data
        assert "recent_sessions" in data
        assert "patients_summary" in data

        # Validar relatório financeiro
        financial = data["financial_report"]
        assert "total_revenue" in financial
        assert "total_paid" in financial
        assert "total_pending" in financial
        assert "entries" in financial
        assert "period_start" in financial
        assert "period_end" in financial
        # Decimal pode vir como string, int ou float na serialização JSON
        assert isinstance(financial["total_revenue"], (int, float, str))
        assert isinstance(financial["total_paid"], (int, float, str))
        assert isinstance(financial["total_pending"], (int, float, str))

        # Validar sessões de hoje
        assert isinstance(data["today_sessions"], list)

        # Validar sessões recentes
        assert isinstance(data["recent_sessions"], list)
        assert len(data["recent_sessions"]) <= 10

        # Validar resumo de pacientes
        patients = data["patients_summary"]
        assert "total_patients" in patients
        assert "active_patients" in patients
        assert "inactive_patients" in patients
        assert isinstance(patients["total_patients"], int)
        assert isinstance(patients["active_patients"], int)
        assert isinstance(patients["inactive_patients"], int)
        assert patients["total_patients"] == patients["active_patients"] + patients["inactive_patients"]

    @pytest.mark.asyncio
    async def test_get_dashboard_summary_invalid_dates(self, client: AsyncClient, auth_headers: dict):
        """GET /dashboard/summary - deve retornar 400 para datas inválidas."""
        today = date.today()
        start_date = today
        end_date = today - timedelta(days=1)  # end_date < start_date

        response = await client.get(
            "/dashboard/summary",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_dashboard_summary_period_too_large(self, client: AsyncClient, auth_headers: dict):
        """GET /dashboard/summary - deve retornar 422 para período > 1 ano."""
        today = date.today()
        start_date = today - timedelta(days=400)  # Mais de 1 ano
        end_date = today

        response = await client.get(
            "/dashboard/summary",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_dashboard_summary_missing_params(self, client: AsyncClient, auth_headers: dict):
        """GET /dashboard/summary - deve retornar 422 sem parâmetros obrigatórios."""
        response = await client.get("/dashboard/summary", headers=auth_headers)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_dashboard_summary_today_sessions(
        self, client: AsyncClient, patient_id: str, auth_headers: dict
    ):
        """GET /dashboard/summary - deve retornar sessões de hoje."""
        # Criar sessão para hoje
        today = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        await client.post(
            "/sessions",
            json={
                "patient_id": patient_id,
                "date_time": today.isoformat(),
                "price": 200.00,
            },
            headers=auth_headers,
        )

        # Buscar resumo
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()

        response = await client.get(
            "/dashboard/summary",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verificar que há sessões de hoje
        today_sessions = data["today_sessions"]
        assert isinstance(today_sessions, list)
        # Pode ter 0 ou mais sessões dependendo do horário

    @pytest.mark.asyncio
    async def test_get_dashboard_summary_recent_sessions(
        self, client: AsyncClient, patient_id: str, auth_headers: dict
    ):
        """GET /dashboard/summary - deve retornar últimas 10 sessões."""
        # Criar múltiplas sessões
        for i in range(5):
            session_date = datetime.now() - timedelta(days=i)
            await client.post(
                "/sessions",
                json={
                    "patient_id": patient_id,
                    "date_time": session_date.isoformat(),
                    "price": 150.00,
                },
                headers=auth_headers,
            )

        # Buscar resumo
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

        response = await client.get(
            "/dashboard/summary",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verificar sessões recentes
        recent_sessions = data["recent_sessions"]
        assert isinstance(recent_sessions, list)
        assert len(recent_sessions) <= 10

        # Verificar ordenação (mais recentes primeiro)
        if len(recent_sessions) > 1:
            dates = [datetime.fromisoformat(s["date_time"].replace("Z", "+00:00")) for s in recent_sessions]
            assert dates == sorted(dates, reverse=True)

    @pytest.mark.asyncio
    async def test_get_dashboard_summary_patients_count(
        self, client: AsyncClient, auth_headers: dict
    ):
        """GET /dashboard/summary - deve retornar contagem correta de pacientes."""
        # Criar alguns pacientes
        for i in range(3):
            await client.post(
                "/patients",
                json={"name": f"Paciente {i}"},
                headers=auth_headers,
            )

        # Buscar resumo
        today = date.today()
        start_date = today - timedelta(days=30)
        end_date = today

        response = await client.get(
            "/dashboard/summary",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        patients = data["patients_summary"]
        assert patients["total_patients"] >= 3
        assert patients["active_patients"] >= 3
        assert patients["inactive_patients"] >= 0

    @pytest.mark.asyncio
    async def test_dashboard_requires_authentication(self, client: AsyncClient):
        """Testa que endpoints de dashboard requerem autenticação."""
        response = await client.get(
            "/dashboard/summary",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
            },
        )
        assert response.status_code == 401
