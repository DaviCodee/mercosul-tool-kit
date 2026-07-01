"""Smoke tests da CLI."""

from __future__ import annotations

from click.testing import CliRunner

from mercosultoolkit.cli.main import app


def test_list_command() -> None:
    """Verifica que 'mtk list' funciona."""
    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "generate" in result.output
    assert "validate" in result.output
    assert "inspect" in result.output


def test_schema_command() -> None:
    """Verifica que 'mtk schema <op>' funciona."""
    runner = CliRunner()
    result = runner.invoke(app, ["schema", "generate"])
    assert result.exit_code == 0
    assert "properties" in result.output


def test_unknown_operation_error() -> None:
    """Verifica que operação desconhecida erra."""
    runner = CliRunner()
    result = runner.invoke(app, ["unknown-op"])
    assert result.exit_code != 0
