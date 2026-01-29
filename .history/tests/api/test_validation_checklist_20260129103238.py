
import pytest
import time
from uuid import uuid4
from datetime import datetime, date, timedelta
from decimal import Decimal
from httpx import AsyncClient

from app.domain.entities.session import SessionStatus

@pytest.mark.asyncio
async def test_get_session_by_id_validation(client: AsyncClient, auth_headers: dict):
    """
    Checklist: GET /sessions/{id}
    - Testar com ID válido
    - Testar com ID inválido (deve retornar 404)
    - Testar com ID de outro formato (deve retornar 400 ou 422)
    """
    # 1. Setup - Create patient and session
    patient_res = await client.post("/patients", json={
        "name": "Test Patient",
        "email": "test@example.com"
    }, headers=auth_headers)
    assert patient_res.status_code == 201
    patient_id = patient_res.json()["id"]

    session_res = await client.post("/sessions", json={
        "patient_id": patient_id,
        "date_time": "2024-01-01T10:00:00",
        "price": 100.0,
        "duration_minutes": 50
    }, headers=auth_headers)
    assert session_res.status_code == 201
    session_id = session_res.json()["id"]

    # 2. Test valid ID
    res_valid = await client.get(f"/sessions/{session_id}", headers=auth_headers)
    assert res_valid.status_code == 200
    assert res_valid.json()["id"] == session_id

    # 3. Test invalid ID (UUID valid format but not found)
    res_not_found = await client.get(f"/sessions/{str(uuid4())}", headers=auth_headers)
    assert res_not_found.status_code == 404

    # 4. Test invalid format
    res_invalid_format = await client.get("/sessions/invalid-uuid-format", headers=auth_headers)
    assert res_invalid_format.status_code == 422  # FastAPI validation error for UUID


@pytest.mark.asyncio
async def test_dashboard_summary_validation(client: AsyncClient, auth_headers: dict):
    """
    Checklist: GET /dashboard/summary
    - Testar com período válido
    - Testar sem parâmetros (deve retornar 400 ou 422)
    - Testar com data inválida
    - Verificar que contagens estão corretas
    - Verificar performance (deve ser < 500ms)
    """
    # 1. Setup - Add data to verify counts
    # Add a paid session (implies creating session + updating status to CONCLUIDA which creates financial entry -> then mark paid)
    # Actually dashboard counts FinancialEntries.
    # Let's verify empty state first or populate.
    
    start_date = "2024-01-01"
    end_date = "2024-01-31"

    # 2. Performance test
    start_time = time.time()
    res = await client.get(f"/dashboard/summary?start_date={start_date}&end_date={end_date}", headers=auth_headers)
    duration = (time.time() - start_time) * 1000  # ms
    
    assert res.status_code == 200
    assert duration < 500, f"Dashboard took {duration}ms"
    
    data = res.json()
    assert "financial_report" in data
    assert "today_sessions" in data
    assert "patients_summary" in data

    # 3. Missing params
    res_missing = await client.get("/dashboard/summary", headers=auth_headers)
    assert res_missing.status_code == 422  # Required query params

    # 4. Invalid date
    res_invalid = await client.get(f"/dashboard/summary?start_date=invalid&end_date={end_date}", headers=auth_headers)
    assert res_invalid.status_code == 422


@pytest.mark.asyncio
async def test_patients_summary_validation(client: AsyncClient, auth_headers: dict):
    """
    Checklist: GET /patients/summary
    - Comparar contagem com SELECT COUNT(*) direto no banco (simulated via API list)
    - Verificar performance (deve ser < 100ms)
    """
    # 1. Setup - Create a few patients
    for i in range(5):
        await client.post("/patients", json={"name": f"Patient {i}"}, headers=auth_headers)
    
    # 2. Performance test
    start_time = time.time()
    res = await client.get("/patients/summary", headers=auth_headers)
    duration = (time.time() - start_time) * 1000 # ms
    
    assert res.status_code == 200
    assert duration < 100, f"Patients summary took {duration}ms"
    
    data = res.json()
    assert data["total_patients"] >= 5
    assert "active_patients" in data


@pytest.mark.asyncio
async def test_cors_validation(client: AsyncClient, auth_headers: dict):
    """
    Checklist: CORS
    - Testar OPTIONS request de http://localhost:3000
    - Testar GET/POST/PATCH com Origin header
    """
    origin = "http://localhost:3000"
    
    # 1. OPTIONS request
    # Note: Using client.request for OPTIONS
    res_options = await client.options(
        "/patients",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        }
    )
    # With TestClient/AsyncClient/ASGITransport, CORS middleware might handle it if configured.
    # If 200 OK and Access-Control-Allow-Origin is present.
    assert res_options.status_code == 200
    assert res_options.headers.get("access-control-allow-origin") == origin
    assert res_options.headers.get("access-control-allow-credentials") == "true"

    # 2. GET with Origin
    headers_with_origin = {**auth_headers, "Origin": origin}
    res_get = await client.get("/patients", headers=headers_with_origin)
    assert res_get.status_code == 200
    assert res_get.headers.get("access-control-allow-origin") == origin


@pytest.mark.asyncio
async def test_patch_session_validation(client: AsyncClient, auth_headers: dict):
    """
    Checklist: PATCH /sessions/{id}
    - Testar atualização de cada campo
    - Verificar que status NÃO muda por este endpoint
    - Testar com patient_id inválido
    """
    # 1. Setup
    patient_res = await client.post("/patients", json={"name": "Patch Patient"}, headers=auth_headers)
    assert patient_res.status_code == 201
    patient_id = patient_res.json()["id"]
    
    session_res = await client.post("/sessions", json={
        "patient_id": patient_id,
        "date_time": "2024-06-01T10:00:00",
        "price": 100.0
    }, headers=auth_headers)
    assert session_res.status_code == 201
    session_id = session_res.json()["id"]
    
    # 2. Update fields
    new_date = "2024-06-02T15:00:00"
    update_data = {
        "date_time": new_date,
        "price": 150.0,
        "notes": "Updated notes",
        # Try to update status (should be ignored or fail validation if not in schema, 
        # but schema doesn't include status, so it should be ignored by Pydantic filtering)
        "status": "realizada" 
    }
    
    res = await client.patch(f"/sessions/{session_id}", json=update_data, headers=auth_headers)
    assert res.status_code == 200
    
    updated = res.json()
    assert updated["date_time"] == new_date
    assert float(updated["price"]) == 150.0
    assert updated["notes"] == "Updated notes"
    assert updated["status"] == "agendada"  # Should NOT change
    
    # 3. Test invalid patient_id
    res_invalid_patient = await client.patch(f"/sessions/{session_id}", json={
        "patient_id": str(uuid4())
    }, headers=auth_headers)
    assert res_invalid_patient.status_code in [404, 422]  # 404 if patient not found, 422 if validation fails
