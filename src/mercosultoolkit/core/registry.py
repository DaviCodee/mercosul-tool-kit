"""Registro central de operações.

As operações se auto-registram via :func:`register`. Os adaptadores percorrem o
registro para expor todas as operações de forma uniforme.
"""

from __future__ import annotations

import importlib
from typing import Any

from mercosultoolkit.core.errors import MercosulToolkitError
from mercosultoolkit.core.operation import DocumentOperation

_REGISTRY: dict[str, DocumentOperation[Any]] = {}
_loaded = False


def register(operation_cls: type[DocumentOperation[Any]]) -> type[DocumentOperation[Any]]:
    """Decorator de classe que instancia e registra uma operação pelo seu ``name``."""
    instance = operation_cls()
    name = instance.name
    if name in _REGISTRY:
        raise MercosulToolkitError(f"operação duplicada no registro: {name!r}")
    _REGISTRY[name] = instance
    return operation_cls


def _ensure_loaded() -> None:
    global _loaded
    if not _loaded:
        _loaded = True
        importlib.import_module("mercosultoolkit.operations")


def get_operation(name: str) -> DocumentOperation[Any]:
    """Retorna a operação registrada com ``name`` ou levanta :class:`MercosulToolkitError`."""
    _ensure_loaded()
    try:
        return _REGISTRY[name]
    except KeyError:
        raise MercosulToolkitError(f"operação desconhecida: {name!r}") from None


def all_operations() -> list[DocumentOperation[Any]]:
    """Retorna todas as operações registradas, ordenadas por nome."""
    _ensure_loaded()
    return [_REGISTRY[name] for name in sorted(_REGISTRY)]
