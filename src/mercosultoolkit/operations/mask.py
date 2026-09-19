"""Operação ``mask``: aplica ou remove máscara de exibição de um documento."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import Field

from mercosultoolkit.core.io import DataInput, OperationResult
from mercosultoolkit.core.operation import DocumentOperation
from mercosultoolkit.core.params import OperationParams
from mercosultoolkit.core.registry import register
from mercosultoolkit.documents.catalog import document_names, get_document
from mercosultoolkit.operations.detect import detect


class MaskParams(OperationParams):
    value: str = Field(min_length=1, description="o documento a mascarar/desmascarar")
    document: str | None = Field(
        default=None,
        description="tipo do documento; se omitido, tenta detectar",
        json_schema_extra={"enum": document_names()},
    )
    to: Literal["masked", "unmasked"] = Field(
        default="masked", description="masked para aplicar máscara, unmasked para remover"
    )


@register
class MaskOperation(DocumentOperation[MaskParams]):
    name = "mask"
    category = "formato"
    summary = "Aplica ou remove máscara de exibição de um documento."
    params_model = MaskParams

    def run(self, inputs: Sequence[DataInput], params: MaskParams) -> OperationResult:
        if params.document:
            doc = get_document(params.document)
        else:
            candidates = detect(params.value)
            if not candidates:
                raise ValueError(f"não foi possível detectar o tipo de {params.value!r}")
            doc = get_document(candidates[0])

        if params.to == "masked":
            raw = doc.strip_mask_value(params.value)
            result = doc.apply_mask(raw)
        else:
            result = doc.strip_mask_value(params.value)

        return OperationResult(
            meta={
                "document": doc.name,
                "from": params.value,
                "to": params.to,
                "result": result,
            }
        )
