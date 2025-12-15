"""Repositórios fake para testes unitários."""

from tests.fakes.fake_repositories import (
    FakePatientRepository,
    FakeSessionRepository,
    FakeFinancialEntryRepository,
)

__all__ = [
    "FakePatientRepository",
    "FakeSessionRepository",
    "FakeFinancialEntryRepository",
]
