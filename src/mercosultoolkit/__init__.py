"""mercosultoolkit — núcleo concentrador de operações sobre documentos do Mercosul.

Expõe um registro de operações genéricas (generate, validate, inspect, mask,
list-documents) consumido pelos adaptadores (CLI, API e GUI futura). O documento concreto
(CPF, CNPJ, DNI, RUT…) é escolhido por parâmetro, a partir de um catálogo de documentos.

O núcleo (``mercosultoolkit.core``) depende só de Pydantic; os documentos
(``mercosultoolkit.documents``) usam apenas a biblioteca padrão.
"""

from mercosultoolkit.core.errors import (
    InvalidInputError,
    MercosulToolkitError,
    MissingDependencyError,
    OperationError,
    UnsupportedFormatError,
)
from mercosultoolkit.core.io import Artifact, DataInput, OperationResult
from mercosultoolkit.core.operation import DocumentOperation
from mercosultoolkit.core.registry import all_operations, get_operation, register

__version__ = "0.1.0"

__all__ = [
    "Artifact",
    "DataInput",
    "DocumentOperation",
    "InvalidInputError",
    "MercosulToolkitError",
    "MissingDependencyError",
    "OperationError",
    "OperationResult",
    "UnsupportedFormatError",
    "all_operations",
    "get_operation",
    "register",
]
