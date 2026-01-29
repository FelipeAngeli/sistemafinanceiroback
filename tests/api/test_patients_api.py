"""Testes de API para endpoints de Pacientes."""

import pytest
from httpx import AsyncClient


class TestPatientsAPI:
    """Testes para /patients endpoints."""

    @pytest.mark.asyncio
    async def test_create_patient_success(self, client: AsyncClient, auth_headers: dict):
        """POST /patients - deve criar paciente."""
        response = await client.post(
            "/patients",
            json={
                "name": "Maria Silva",
                "email": "maria@email.com",
                "phone": "(11) 99999-9999",
                "observation": "Paciente teste",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Maria Silva"
        assert data["email"] == "maria@email.com"
        assert data["observation"] == "Paciente teste"
        assert data["active"] is True
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_patient_minimal(self, client: AsyncClient, auth_headers: dict):
        """POST /patients - deve criar paciente apenas com nome."""
        response = await client.post(
            "/patients",
            json={"name": "João Santos"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "João Santos"
        assert data["email"] is None

    @pytest.mark.asyncio
    async def test_create_patient_validation_error(self, client: AsyncClient, auth_headers: dict):
        """POST /patients - deve retornar erro se nome vazio."""
        response = await client.post(
            "/patients",
            json={"name": ""},
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_patients(self, client: AsyncClient, auth_headers: dict):
        """GET /patients - deve listar pacientes."""
        # Criar alguns pacientes
        await client.post("/patients", json={"name": "Paciente 1"}, headers=auth_headers)
        await client.post("/patients", json={"name": "Paciente 2"}, headers=auth_headers)

        response = await client.get("/patients", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "patients" in data
        assert "total" in data
        assert data["total"] >= 2

    @pytest.mark.asyncio
    async def test_get_patient_by_id(self, client: AsyncClient, auth_headers: dict):
        """GET /patients/{id} - deve retornar paciente."""
        # Criar paciente
        create_response = await client.post(
            "/patients",
            json={"name": "Ana Paula", "email": "ana@email.com"},
            headers=auth_headers,
        )
        patient_id = create_response.json()["id"]

        # Buscar
        response = await client.get(f"/patients/{patient_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == patient_id
        assert data["name"] == "Ana Paula"

    @pytest.mark.asyncio
    async def test_get_patient_not_found(self, client: AsyncClient, auth_headers: dict):
        """GET /patients/{id} - deve retornar 404 se não existe."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/patients/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_patients_require_authentication(self, client: AsyncClient):
        """Testa que endpoints de pacientes requerem autenticação."""
        # Tentar criar paciente sem token
        response = await client.post(
            "/patients",
            json={"name": "Teste"},
        )
        assert response.status_code == 401

        # Tentar listar pacientes sem token
        response = await client.get("/patients")
        assert response.status_code == 401

        # Tentar buscar paciente sem token
        response = await client.get("/patients/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 401
