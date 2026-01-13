"""Testes para entrypoints principais da aplicação."""

import importlib
import sys
import types

import pytest


def _reload(module_name: str):
    if module_name in sys.modules:
        del sys.modules[module_name]
    return importlib.import_module(module_name)


def _ensure_dummy_mangum(monkeypatch):
    dummy_module = types.ModuleType("mangum")

    class DummyMangum:
        def __init__(self, app, **kwargs):
            self.app = app

    dummy_module.Mangum = DummyMangum
    monkeypatch.setitem(sys.modules, "mangum", dummy_module)


def test_main_app_exposes_fastapi_instance():
    module = _reload("app.main")
    assert hasattr(module, "app"), "app.main deve expor objeto FastAPI"


def test_lambda_handler_creates_mangum_handler(monkeypatch):
    _ensure_dummy_mangum(monkeypatch)
    monkeypatch.setitem(sys.modules, "app.interfaces.http.api", types.SimpleNamespace(create_app=lambda: object()))
    module = _reload("app.lambda_handler")
    assert hasattr(module, "handler"), "lambda_handler deve expor handler Mangum"
