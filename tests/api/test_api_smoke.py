"""Smoke tests da API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from mercosultoolkit.api.app import app

client = TestClient(app)


def test_list_operations() -> None:
    """Verifica que GET /operations funciona."""
    response = client.get("/operations")
    assert response.status_code == 200
    ops = response.json()
    assert isinstance(ops, list)
    assert len(ops) > 0
    assert any(op["name"] == "generate" for op in ops)


def test_operation_schema() -> None:
    """Verifica que GET /operations/{name}/schema funciona."""
    response = client.get("/operations/generate/schema")
    assert response.status_code == 200
    schema = response.json()
    assert "properties" in schema


def test_unknown_operation_404() -> None:
    """Verifica que operação desconhecida retorna 404."""
    response = client.get("/operations/unknown-op/schema")
    assert response.status_code == 404
