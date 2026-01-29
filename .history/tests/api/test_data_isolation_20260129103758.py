"""Testes de isolamento de dados entre usuários.

Valida que usuários só podem acessar seus próprios dados.
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient


class TestDataIsolation:
    """Testes de isolamento de dados entre usuários."""

    @pytest.fixture
    async def user1_token(self, client: AsyncClient) -> str:
        """Cria usuário 1 e retorna token."""
        # Registrar usuário 1
        await client.post(
            "/auth/register",
            json={
                "email": "user1@test.com",
                "password": "senha123",
                "name": "Usuário 1",
            },
        )

        # Login usuário 1
        response = await client.post(
            "/auth/login",
            json={
                "email": "user1@test.com",
                "password": "senha123",
            },
        )
        return response.json()["access_token"]

    @pytest.fixture
    async def user2_token(self, client: AsyncClient) -> str:
        """Cria usuário 2 e retorna token."""
        # Gerar email único para evitar conflitos
        unique_email = f"user2_{uuid4().hex[:8]}@test.com"
        
        # Registrar usuário 2
        await client.post(
            "/auth/register",
            json={
                "email": unique_email,
                "password": "senha123",
                "name": "Usuário 2",
            },
        )

        # Login usuário 2
        response = await client.post(
            "/auth/login",
            json={
                "email": unique_email,
                "password": "senha123",
            },
        )
        return response.json()["access_token"]

    @pytest.fixture
    async def user1_patient_id(
        self, client: AsyncClient, user1_token: str
    ) -> str:
        """Cria paciente para usuário 1 e retorna ID."""
        response = await client.post(
            "/patients",
            json={"name": "Paciente User 1"},
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        return response.json()["id"]

    @pytest.fixture
    async def user2_patient_id(
        self, client: AsyncClient, user2_token: str
    ) -> str:
        """Cria paciente para usuário 2 e retorna ID."""
        response = await client.post(
            "/patients",
            json={"name": "Paciente User 2"},
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        return response.json()["id"]

    # ============================================================
    # Testes de Isolamento de Pacientes
    # ============================================================

    @pytest.mark.asyncio
    async def test_user_cannot_see_other_user_patients(
        self, client: AsyncClient, user1_token: str, user2_token: str
    ):
        """Usuário 1 não deve ver pacientes de Usuário 2."""
        # Criar paciente para usuário 2
        await client.post(
            "/patients",
            json={"name": "Paciente User 2"},
            headers={"Authorization": f"Bearer {user2_token}"},
        )

        # Usuário 1 lista seus pacientes (deve estar vazio)
        response = await client.get(
            "/patients",
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["patients"]) == 0

    @pytest.mark.asyncio
    async def test_user_can_only_see_own_patients(
        self, client: AsyncClient, user1_token: str, user2_token: str
    ):
        """Cada usuário só vê seus próprios pacientes."""
        # Criar pacientes para usuário 1
        await client.post(
            "/patients",
            json={"name": "Paciente 1 User 1"},
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        await client.post(
            "/patients",
            json={"name": "Paciente 2 User 1"},
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        # Criar pacientes para usuário 2
        await client.post(
            "/patients",
            json={"name": "Paciente 1 User 2"},
            headers={"Authorization": f"Bearer {user2_token}"},
        )

        # Usuário 1 lista seus pacientes
        response1 = await client.get(
            "/patients",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["total"] == 2
        assert all("Paciente" in p["name"] and "User 1" in p["name"] for p in data1["patients"])

        # Usuário 2 lista seus pacientes
        response2 = await client.get(
            "/patients",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 1
        assert all("User 2" in p["name"] for p in data2["patients"])

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_user_patient_by_id(
        self,
        client: AsyncClient,
        user1_token: str,
        user2_token: str,
        user2_patient_id: str,
    ):
        """Usuário 1 não pode acessar paciente de Usuário 2 por ID."""
        # Usuário 1 tenta acessar paciente de usuário 2
        response = await client.get(
            f"/patients/{user2_patient_id}",
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_user_can_access_own_patient_by_id(
        self,
        client: AsyncClient,
        user1_token: str,
        user1_patient_id: str,
    ):
        """Usuário pode acessar seu próprio paciente por ID."""
        response = await client.get(
            f"/patients/{user1_patient_id}",
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user1_patient_id

    @pytest.mark.asyncio
    async def test_patient_summary_is_isolated(
        self, client: AsyncClient, user1_token: str, user2_token: str
    ):
        """Estatísticas de pacientes são isoladas por usuário."""
        # Criar 3 pacientes para usuário 1
        for i in range(3):
            await client.post(
                "/patients",
                json={"name": f"Paciente {i} User 1"},
                headers={"Authorization": f"Bearer {user1_token}"},
            )

        # Criar 2 pacientes para usuário 2
        for i in range(2):
            await client.post(
                "/patients",
                json={"name": f"Paciente {i} User 2"},
                headers={"Authorization": f"Bearer {user2_token}"},
            )

        # Usuário 1 vê apenas seus 3 pacientes
        response1 = await client.get(
            "/patients/summary",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert response1.status_code == 200
        assert response1.json()["total"] == 3

        # Usuário 2 vê apenas seus 2 pacientes
        response2 = await client.get(
            "/patients/summary",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert response2.status_code == 200
        assert response2.json()["total"] == 2

    # ============================================================
    # Testes de Isolamento de Sessões
    # ============================================================

    @pytest.mark.asyncio
    async def test_user_cannot_create_session_for_other_user_patient(
        self,
        client: AsyncClient,
        user1_token: str,
        user2_token: str,
        user2_patient_id: str,
    ):
        """Usuário 1 não pode criar sessão para paciente de Usuário 2."""
        response = await client.post(
            "/sessions",
            json={
                "patient_id": user2_patient_id,
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
            },
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        assert response.status_code == 404  # Paciente não encontrado para este usuário

    @pytest.mark.asyncio
    async def test_user_can_create_session_for_own_patient(
        self,
        client: AsyncClient,
        user1_token: str,
        user1_patient_id: str,
    ):
        """Usuário pode criar sessão para seu próprio paciente."""
        response = await client.post(
            "/sessions",
            json={
                "patient_id": user1_patient_id,
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
            },
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["patient_id"] == user1_patient_id

    @pytest.mark.asyncio
    async def test_user_cannot_see_other_user_sessions(
        self,
        client: AsyncClient,
        user1_token: str,
        user2_token: str,
        user2_patient_id: str,
    ):
        """Usuário 1 não vê sessões de Usuário 2."""
        # Criar sessão para usuário 2
        await client.post(
            "/sessions",
            json={
                "patient_id": user2_patient_id,
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
            },
            headers={"Authorization": f"Bearer {user2_token}"},
        )

        # Usuário 1 lista suas sessões (deve estar vazio)
        response = await client.get(
            "/sessions",
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["sessions"]) == 0

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_user_session_by_id(
        self,
        client: AsyncClient,
        user1_token: str,
        user2_token: str,
        user2_patient_id: str,
    ):
        """Usuário 1 não pode acessar sessão de Usuário 2 por ID."""
        # Criar sessão para usuário 2
        create_response = await client.post(
            "/sessions",
            json={
                "patient_id": user2_patient_id,
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
            },
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        session_id = create_response.json()["id"]

        # Usuário 1 tenta acessar sessão de usuário 2
        response = await client.get(
            f"/sessions/{session_id}",
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        assert response.status_code == 404

    # ============================================================
    # Testes de Autenticação Obrigatória
    # ============================================================

    @pytest.mark.asyncio
    async def test_endpoints_require_authentication(self, client: AsyncClient):
        """Endpoints protegidos devem retornar 401 sem token."""
        # Listar pacientes sem token
        response = await client.get("/patients")
        assert response.status_code == 401

        # Criar paciente sem token
        response = await client.post("/patients", json={"name": "Teste"})
        assert response.status_code == 401

        # Listar sessões sem token
        response = await client.get("/sessions")
        assert response.status_code == 401

        # Criar sessão sem token
        response = await client.post(
            "/sessions",
            json={
                "patient_id": "00000000-0000-0000-0000-000000000000",
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401(self, client: AsyncClient):
        """Token inválido deve retornar 401."""
        response = await client.get(
            "/patients",
            headers={"Authorization": "Bearer token-invalido"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient):
        """Requisição sem token deve retornar 401."""
        response = await client.get("/patients")
        assert response.status_code == 401

    # ============================================================
    # Testes de Integração Completa
    # ============================================================

    @pytest.mark.asyncio
    async def test_complete_isolation_workflow(
        self, client: AsyncClient, user1_token: str, user2_token: str
    ):
        """Teste completo de isolamento: registro -> criar dados -> verificar isolamento."""
        # Usuário 1 cria paciente e sessão
        patient1_response = await client.post(
            "/patients",
            json={"name": "Paciente Completo User 1"},
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        patient1_id = patient1_response.json()["id"]

        session1_response = await client.post(
            "/sessions",
            json={
                "patient_id": patient1_id,
                "date_time": "2024-12-15T14:00:00",
                "price": 200.00,
            },
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        session1_id = session1_response.json()["id"]

        # Usuário 2 cria paciente e sessão
        patient2_response = await client.post(
            "/patients",
            json={"name": "Paciente Completo User 2"},
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        patient2_id = patient2_response.json()["id"]

        session2_response = await client.post(
            "/sessions",
            json={
                "patient_id": patient2_id,
                "date_time": "2024-12-16T15:00:00",
                "price": 250.00,
            },
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        session2_id = session2_response.json()["id"]

        # Usuário 1 só vê seus próprios dados
        patients1 = await client.get(
            "/patients",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert patients1.json()["total"] == 1
        assert patients1.json()["patients"][0]["id"] == patient1_id

        sessions1 = await client.get(
            "/sessions",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert sessions1.json()["total"] == 1
        assert sessions1.json()["sessions"][0]["id"] == session1_id

        # Usuário 2 só vê seus próprios dados
        patients2 = await client.get(
            "/patients",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert patients2.json()["total"] == 1
        assert patients2.json()["patients"][0]["id"] == patient2_id

        sessions2 = await client.get(
            "/sessions",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert sessions2.json()["total"] == 1
        assert sessions2.json()["sessions"][0]["id"] == session2_id

        # Usuário 1 não pode acessar dados de usuário 2
        patient2_access = await client.get(
            f"/patients/{patient2_id}",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert patient2_access.status_code == 404

        session2_access = await client.get(
            f"/sessions/{session2_id}",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert session2_access.status_code == 404
