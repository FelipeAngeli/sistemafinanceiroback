"""Testes para FinancialEntryMapper."""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from app.domain.entities.financial_entry import EntryStatus, FinancialEntry
from app.infra.db.mappers.financial_entry_mapper import FinancialEntryMapper
from app.infra.db.models.financial_entry_model import FinancialEntryModel


def _make_entry(status: EntryStatus = EntryStatus.PENDENTE) -> FinancialEntry:
    return FinancialEntry(
        id=uuid4(),
        session_id=uuid4(),
        patient_id=uuid4(),
        user_id=uuid4(),
        amount=Decimal("199.90"),
        entry_date=date.today(),
        description="Descrição",
        status=status,
    )


def test_to_model_maps_all_fields():
    entry = _make_entry()

    model = FinancialEntryMapper.to_model(entry)

    assert model.id == str(entry.id)
    assert model.session_id == str(entry.session_id)
    assert model.patient_id == str(entry.patient_id)
    assert model.amount == entry.amount
    assert model.entry_date == entry.entry_date
    assert model.description == entry.description
    assert model.status == entry.status.value
    assert model.paid_at == entry.paid_at


def test_to_entity_restores_domain_values():
    model = FinancialEntryModel(
        id=str(uuid4()),
        session_id=str(uuid4()),
        patient_id=str(uuid4()),
        user_id=str(uuid4()),
        amount=Decimal("250.00"),
        entry_date=date.today(),
        description="Teste",
        status=EntryStatus.PAGO.value,
        created_at=datetime.now(UTC),
        paid_at=datetime.now(UTC),
    )

    entity = FinancialEntryMapper.to_entity(model)

    assert str(entity.id) == model.id
    assert str(entity.session_id) == model.session_id
    assert entity.amount == Decimal("250.00")
    assert entity.status == EntryStatus.PAGO
    assert entity.description == model.description
    assert entity.paid_at == model.paid_at


def test_update_model_writes_changes():
    model = FinancialEntryModel(
        id=str(uuid4()),
        session_id=str(uuid4()),
        patient_id=str(uuid4()),
        user_id=str(uuid4()),
        amount=Decimal("100.00"),
        entry_date=date.today(),
        description="",
        status=EntryStatus.PENDENTE.value,
        created_at=datetime.now(UTC),
        paid_at=None,
    )
    entry = _make_entry()
    entry.mark_as_paid()

    FinancialEntryMapper.update_model(model, entry)

    assert model.amount == entry.amount
    assert model.description == entry.description
    assert model.status == entry.status.value
    assert model.paid_at == entry.paid_at
