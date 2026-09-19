"""Operação ``generate``: cria um ou mais documentos de um tipo."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import Field

from mercosultoolkit.core.io import DataInput, OperationResult
from mercosultoolkit.core.operation import DocumentOperation
from mercosultoolkit.core.params import OperationParams
from mercosultoolkit.core.registry import register
from mercosultoolkit.documents.base import GenContext
from mercosultoolkit.documents.catalog import document_names, get_document


class GenerateParams(OperationParams):
    """Parâmetros da geração. Cada documento lê só os campos que lhe interessam."""

    document: str = Field(
        min_length=1,
        description="tipo de documento (ex.: cpf, cnpj, rut-cl)",
        json_schema_extra={"enum": document_names()},
    )
    count: int = Field(default=1, ge=1, le=10_000, description="quantos documentos gerar")
    masked: bool = Field(default=True, description="aplica máscara de exibição na saída")
    uf: str | None = Field(
        default=None,
        description="Título de Eleitor: UF; outros: região se aplicável",
    )
    kind: str | None = Field(
        default=None,
        description="CNS/CUIT/CNPJ/Pix: variante (veja help de cada operação)",
    )
    plate_format: str | None = Field(
        default=None, description="placas/veicular: old|mercosul|new"
    )
    seed: int | None = Field(
        default=None, description="semente para geração determinística (testes)"
    )


@register
class GenerateOperation(DocumentOperation[GenerateParams]):
    name = "generate"
    category = "geração"
    summary = "Gera um ou mais documentos de um tipo."
    params_model = GenerateParams

    def run(self, inputs: Sequence[DataInput], params: GenerateParams) -> OperationResult:
        document = get_document(params.document)
        ctx = GenContext(
            uf=params.uf,
            kind=params.kind,
            plate_format=params.plate_format,
            seed=params.seed,
        )
        values = [document.generate(ctx) for _ in range(params.count)]
        if params.masked:
            values = [document.apply_mask(v) for v in values]
        return OperationResult(
            meta={
                "document": document.name,
                "country": document.country,
                "count": len(values),
                "values": values,
            }
        )
