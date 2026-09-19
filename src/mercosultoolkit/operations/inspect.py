"""Operação ``inspect``: extrai metadados de um documento (componentes, DVs…)."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import Field

from mercosultoolkit.core.errors import InvalidInputError
from mercosultoolkit.core.io import DataInput, OperationResult
from mercosultoolkit.core.operation import DocumentOperation
from mercosultoolkit.core.params import OperationParams
from mercosultoolkit.core.registry import register
from mercosultoolkit.documents.catalog import document_names, get_document
from mercosultoolkit.operations.detect import detect


class InspectParams(OperationParams):
    value: str = Field(min_length=1, description="o documento a inspecionar")
    document: str | None = Field(
        default=None,
        description="tipo do valor; se omitido, tenta detectar",
        json_schema_extra={"enum": document_names()},
    )


@register
class InspectOperation(DocumentOperation[InspectParams]):
    name = "inspect"
    category = "análise"
    summary = "Extrai metadados de um documento (componentes, dígitos verificadores)."
    params_model = InspectParams

    def run(self, inputs: Sequence[DataInput], params: InspectParams) -> OperationResult:
        if params.document:
            doc = get_document(params.document)
            info = doc.parse(params.value)
            return OperationResult(meta={"valid": True, "detected": doc.name, **info})

        candidates = detect(params.value)
        if not candidates:
            raise InvalidInputError(
                f"não foi possível detectar o tipo de {params.value!r}; "
                "informe 'document' explicitamente"
            )
        best = candidates[0]
        parsed = get_document(best).parse(params.value)
        return OperationResult(
            meta={"valid": True, "detected": best, "candidates": candidates, **parsed}
        )
