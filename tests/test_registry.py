"""Testes do registro de operações."""

from __future__ import annotations

from mercosultoolkit.core.registry import all_operations


def test_all_operations_registered() -> None:
    """Verifica que todas as operações estão registradas."""
    ops = all_operations()
    names = [op.name for op in ops]
    assert "generate" in names
    assert "validate" in names
    assert "inspect" in names
    assert "mask" in names
    assert "list-documents" in names


def test_operations_have_correct_inputs() -> None:
    """Verifica que todas as operações declaram min/max_inputs == 0."""
    for op in all_operations():
        assert op.min_inputs == 0, f"{op.name} deve ter min_inputs == 0"
        assert op.max_inputs == 0, f"{op.name} deve ter max_inputs == 0"
