"""Contrato base de uma operação sobre documentos.

Toda operação é uma classe que declara metadados (nome, categoria, resumo), o modelo
de parâmetros e quantas entradas aceita, além de implementar ``run``.

Como documentos são texto, o valor de entrada (quando há) chega via campo do modelo
de parâmetros — não por arquivo. Por isso as operações deste toolkit usam
``min_inputs = max_inputs = 0``. O contrato continua aceitando ``inputs`` para manter
paridade estrutural com os projetos irmãos e permitir entradas em arquivo no futuro.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import ClassVar, Generic, TypeVar

from mercosultoolkit.core.errors import InvalidInputError
from mercosultoolkit.core.io import DataInput, OperationResult
from mercosultoolkit.core.params import OperationParams

P = TypeVar("P", bound=OperationParams)


class DocumentOperation(ABC, Generic[P]):
    """Unidade de trabalho do toolkit.

    Subclasses fixam o tipo de parâmetro via ``DocumentOperation[MeusParams]`` e definem
    os atributos de classe abaixo.
    """

    name: ClassVar[str]
    category: ClassVar[str]
    summary: ClassVar[str]
    params_model: ClassVar[type[OperationParams]]
    min_inputs: ClassVar[int] = 0
    max_inputs: ClassVar[int | None] = 0

    def check_inputs(self, inputs: Sequence[DataInput]) -> None:
        """Valida a quantidade de entradas."""
        count = len(inputs)
        if count < self.min_inputs:
            raise InvalidInputError(
                f"operação {self.name!r} exige ao menos {self.min_inputs} entrada(s), "
                f"recebeu {count}"
            )
        if self.max_inputs is not None and count > self.max_inputs:
            raise InvalidInputError(
                f"operação {self.name!r} aceita no máximo {self.max_inputs} entrada(s), "
                f"recebeu {count}"
            )

    @abstractmethod
    def run(self, inputs: Sequence[DataInput], params: P) -> OperationResult:
        """Executa a operação e devolve o resultado."""

    def execute(self, inputs: Sequence[DataInput], params: P) -> OperationResult:
        """Valida as entradas e chama :meth:`run`."""
        self.check_inputs(inputs)
        return self.run(inputs, params)
