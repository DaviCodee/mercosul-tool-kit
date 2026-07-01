"""Tipos de entrada e saída compartilhados pelas operações.

Documentos são essencialmente texto e metadados, então o resultado de uma operação
viaja em ``OperationResult.meta``. Os tipos de artefato ficam disponíveis para o caso de
uma operação querer materializar uma saída em arquivo (ex.: gerar documentos em lote para um
``.txt``), mantendo o mesmo contrato dos projetos irmãos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mercosultoolkit.core.errors import OperationError


@dataclass(slots=True)
class DataInput:
    """Uma entrada: bytes brutos mais um nome de origem opcional."""

    data: bytes
    name: str = "entrada.bin"


@dataclass(slots=True)
class Artifact:
    """Um arquivo produzido por uma operação."""

    data: bytes
    filename: str
    media_type: str = "application/octet-stream"


@dataclass(slots=True)
class OperationResult:
    """Resultado de uma operação: metadados (o caso comum) e zero ou mais artefatos."""

    artifacts: list[Artifact] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def single(self) -> Artifact:
        """Retorna o único artefato; erro se houver zero ou mais de um."""
        if len(self.artifacts) != 1:
            raise OperationError(f"esperado 1 artefato, obtido {len(self.artifacts)}")
        return self.artifacts[0]
