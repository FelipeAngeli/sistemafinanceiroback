"""Testes de API para endpoints de Health."""

import pytest
from httpx import AsyncClient


class TestHealthAPI:
    """Testes para endpoints de health check."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """GET / - deve retornar info da API."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert "version" in data
        assert data["version"] == "0.1.0"

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """GET /health - deve retornar status healthy."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_docs_available(self, client: AsyncClient):
        """GET /docs - documentação deve estar disponível."""
        response = await client.get("/docs")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_openapi_schema(self, client: AsyncClient):
        """GET /openapi.json - schema deve estar disponível."""
        response = await client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
