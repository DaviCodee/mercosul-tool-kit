"""Operação ``validate``: confere se um valor é um documento válido (ou detecta o tipo)."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import Field

from mercosultoolkit.core.io import DataInput, OperationResult
from mercosultoolkit.core.operation import DocumentOperation
from mercosultoolkit.core.params import OperationParams
from mercosultoolkit.core.registry import register
from mercosultoolkit.documents.catalog import document_names, get_document
from mercosultoolkit.operations.detect import detect


class ValidateParams(OperationParams):
    value: str = Field(min_length=1, description="o documento a validar")
    document: str | None = Field(
        default=None,
        description="valida contra este documento; se omitido, tenta detectar",
        json_schema_extra={"enum": document_names()},
    )


@register
class ValidateOperation(DocumentOperation[ValidateParams]):
    name = "validate"
    category = "análise"
    summary = "Verifica se um valor é um documento válido (ou detecta o tipo provável)."
    params_model = ValidateParams

    def run(self, inputs: Sequence[DataInput], params: ValidateParams) -> OperationResult:
        if params.document:
            doc = get_document(params.document)
            valid = doc.validate(params.value)
            return OperationResult(
                meta={
                    "value": params.value,
                    "document": doc.name,
                    "valid": valid,
                    "detected": doc.name if valid else None,
                }
            )

        candidates = detect(params.value)
        return OperationResult(
            meta={
                "value": params.value,
                "document": None,
                "valid": bool(candidates),
                "detected": candidates[0] if candidates else None,
                "candidates": candidates,
            }
        )
