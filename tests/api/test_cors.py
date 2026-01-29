"""Testes para validação de CORS e requisições OPTIONS.

Este módulo testa:
- Requisições OPTIONS para rotas existentes
- Requisições OPTIONS para rotas inexistentes (não devem retornar 400)
- Headers CORS corretos
- Diferentes origens permitidas
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_options_existing_route(client: AsyncClient):
    """Testa OPTIONS request para uma rota existente."""
    origin = "http://localhost:3000"
    
    response = await client.options(
        "/auth/login",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }
    )
    
    # Deve retornar 200, não 400 ou 405
    assert response.status_code == 200, f"Esperado 200, recebido {response.status_code}"
    
    # Deve ter headers CORS
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == origin
    
    # Deve permitir credentials se origem estiver na lista permitida
    if origin in ["http://localhost:3000"]:
        assert response.headers.get("access-control-allow-credentials") == "true"
    
    # Deve ter métodos permitidos
    assert "access-control-allow-methods" in response.headers
    assert "OPTIONS" in response.headers["access-control-allow-methods"]


@pytest.mark.asyncio
async def test_options_nonexistent_route(client: AsyncClient):
    """Testa OPTIONS request para uma rota inexistente (não deve retornar 400).
    
    Este teste valida o bug corrigido onde OPTIONS para /config/settings
    estava retornando 400 em vez de 200.
    """
    origin = "http://localhost:3000"
    
    # Testa a rota que estava dando erro nos logs
    response = await client.options(
        "/config/settings",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        }
    )
    
    # CRÍTICO: Não deve retornar 400 (Bad Request)
    assert response.status_code != 400, (
        f"OPTIONS request retornou 400. Isso indica problema com CORS. "
        f"Headers recebidos: {dict(response.headers)}"
    )
    
    # Deve retornar 200 (OK) para permitir preflight
    assert response.status_code == 200, (
        f"Esperado 200 para OPTIONS, recebido {response.status_code}. "
        f"Response: {response.text}"
    )
    
    # Deve ter headers CORS mesmo para rota inexistente
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == origin


@pytest.mark.asyncio
async def test_options_multiple_nonexistent_routes(client: AsyncClient):
    """Testa OPTIONS para várias rotas inexistentes."""
    origin = "http://localhost:3000"
    
    nonexistent_routes = [
        "/config/settings",
        "/api/v1/users",
        "/nonexistent/endpoint",
        "/another/missing/route",
    ]
    
    for route in nonexistent_routes:
        response = await client.options(
            route,
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            }
        )
        
        # Todas devem retornar 200, não 400
        assert response.status_code == 200, (
            f"Rota {route} retornou {response.status_code} em vez de 200"
        )
        
        # Todas devem ter headers CORS
        assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_options_with_different_allowed_origins(client: AsyncClient):
    """Testa OPTIONS com diferentes origens permitidas."""
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://sistemafinanceiropsico-6cf04.web.app",
    ]
    
    for origin in allowed_origins:
        response = await client.options(
            "/patients",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            }
        )
        
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
        assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_options_without_origin_header(client: AsyncClient):
    """Testa OPTIONS sem header Origin (requisição não-CORS)."""
    response = await client.options(
        "/auth/login",
        headers={
            "Access-Control-Request-Method": "POST",
        }
    )
    
    # Deve retornar 200 mesmo sem Origin
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_cors_headers_on_get_request(client: AsyncClient):
    """Testa que requisições GET também retornam headers CORS."""
    origin = "http://localhost:3000"
    
    response = await client.get(
        "/health",
        headers={"Origin": origin}
    )
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == origin


@pytest.mark.asyncio
async def test_cors_headers_on_post_request(client: AsyncClient):
    """Testa que requisições POST também retornam headers CORS."""
    origin = "http://localhost:3000"
    
    response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
        headers={"Origin": origin}
    )
    
    # Mesmo que a autenticação falhe, deve ter headers CORS
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == origin


@pytest.mark.asyncio
async def test_options_with_preflight_headers(client: AsyncClient):
    """Testa OPTIONS com todos os headers de preflight CORS."""
    origin = "http://localhost:3000"
    
    response = await client.options(
        "/patients",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization",
        }
    )
    
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers
    
    # Deve incluir os métodos e headers solicitados
    allowed_methods = response.headers["access-control-allow-methods"]
    assert "POST" in allowed_methods or "*" in allowed_methods
    
    allowed_headers = response.headers["access-control-allow-headers"]
    assert "*" in allowed_headers or "content-type" in allowed_headers.lower()
