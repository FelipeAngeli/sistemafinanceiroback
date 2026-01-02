"""Testes para DatabaseConnection singleton."""

import pytest

from app.infra.database.connection import DatabaseConnection


def test_database_connection_singleton():
    conn1 = DatabaseConnection.get_instance()
    conn2 = DatabaseConnection.get_instance()
    assert conn1 is conn2
