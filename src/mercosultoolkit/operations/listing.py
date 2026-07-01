"""Operação ``list-documents``: lista o catálogo de documentos."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import Field

from mercosultoolkit.core.io import DataInput, OperationResult
from mercosultoolkit.core.operation import DocumentOperation
from mercosultoolkit.core.params import OperationParams
from mercosultoolkit.core.registry import register
from mercosultoolkit.documents.catalog import all_documents, documents_by_country


class ListDocumentsParams(OperationParams):
    country: str | None = Field(
        default=None, description="filtrar por país (BR, AR, UY, PY, CL)"
    )


@register
class ListDocumentsOperation(DocumentOperation[ListDocumentsParams]):
    name = "list-documents"
    category = "catálogo"
    summary = "Lista os documentos disponíveis."
    params_model = ListDocumentsParams

    def run(self, inputs: Sequence[DataInput], params: ListDocumentsParams) -> OperationResult:
        if params.country:
            docs = documents_by_country(params.country)
        else:
            docs = all_documents()

        documents = [
            {
                "name": doc.name,
                "country": doc.country,
                "family": doc.family,
                "mask": doc.mask,
                "summary": doc.summary,
                "available": doc.available,
                "reason": doc.reason,
            }
            for doc in docs
        ]
        return OperationResult(meta={"documents": documents})
