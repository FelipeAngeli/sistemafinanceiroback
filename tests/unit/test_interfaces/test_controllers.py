"""Testes básicos para controllers HTTP (stubs)."""

from uuid import uuid4

import pytest

from app.interfaces.http.financial_controller import FinancialController
from app.interfaces.http.health_controller import HealthController
from app.interfaces.http.patient_controller import PatientController
from app.interfaces.http.session_controller import SessionController


@pytest.mark.asyncio
async def test_patient_controller_methods_return_none():
    controller = PatientController()
    patient_id = uuid4()

    assert await controller.create({"name": "Test"}) is None
    assert await controller.get(patient_id) is None
    assert await controller.list() is None
    assert await controller.update(patient_id, {"name": "Updated"}) is None
    assert await controller.delete(patient_id) is None


@pytest.mark.asyncio
async def test_financial_controller_methods_return_none():
    controller = FinancialController()
    entry_id = uuid4()

    assert await controller.list() is None
    assert await controller.get(entry_id) is None
    assert await controller.mark_as_paid(entry_id) is None


@pytest.mark.asyncio
async def test_session_controller_methods_return_none():
    controller = SessionController()
    session_id = uuid4()

    assert await controller.schedule({"patient_id": str(uuid4())}) is None
    assert await controller.get(session_id) is None
    assert await controller.list(patient_id=uuid4(), status="agendada") is None
    assert await controller.complete(session_id) is None
    assert await controller.cancel(session_id) is None


@pytest.mark.asyncio
async def test_health_controller_methods():
    controller = HealthController()

    assert await controller.health() == {"status": "healthy"}
    assert await controller.ready() == {"status": "ready"}
