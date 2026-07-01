"""Fixtures compartilhadas."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from mercosultoolkit.core.io import OperationResult
from mercosultoolkit.core.registry import get_operation


@pytest.fixture
def run_op() -> Callable[..., OperationResult]:
    def _run(op_name: str, /, **params: object) -> OperationResult:
        op = get_operation(op_name)
        return op.execute([], op.params_model(**params))

    return _run
