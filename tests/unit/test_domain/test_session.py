"""
Testes para entidade Session.
"""

import pytest
from app.domain.entities.session import Session, SessionStatus


class TestSession:
    """Testes da entidade Session."""

    def test_create_session_with_scheduled_status(self):
        """Deve criar sessão com status agendado."""
        pass

    def test_complete_session(self):
        """Deve concluir sessão corretamente."""
        pass

    def test_cancel_session(self):
        """Deve cancelar sessão corretamente."""
        pass
