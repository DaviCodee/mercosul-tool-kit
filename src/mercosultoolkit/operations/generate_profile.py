"""Operação ``generate-profile``: cria um perfil fake de pessoa ou empresa."""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import Literal

from pydantic import Field

from mercosultoolkit.core.io import DataInput, OperationResult
from mercosultoolkit.core.operation import DocumentOperation
from mercosultoolkit.core.params import OperationParams
from mercosultoolkit.core.registry import register
from mercosultoolkit.fake.profile import build_pessoa, build_empresa


class ProfileParams(OperationParams):
    """Parâmetros de geração de perfil fake."""

    kind: Literal["pessoa", "empresa"] = Field(
        description="tipo de perfil: pessoa ou empresa"
    )
    country: str = Field(
        default="BR",
        min_length=2,
        max_length=2,
        description="código ISO 3166-1 alpha-2 do país (ex.: BR)",
    )
    count: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="quantos perfis gerar",
    )
    seed: int | None = Field(
        default=None,
        description="semente para geração determinística (testes)",
    )


@register
class GenerateProfileOperation(DocumentOperation[ProfileParams]):
    name = "generate-profile"
    category = "geração"
    summary = "Gera um perfil fake de pessoa ou empresa para testes."
    params_model = ProfileParams

    def run(self, inputs: Sequence[DataInput], params: ProfileParams) -> OperationResult:
        rng = random.Random(params.seed)
        profiles = []

        for _ in range(params.count):
            if params.kind == "pessoa":
                profile = build_pessoa(params.country, rng)
                profiles.append(profile["pessoa"])
            else:
                profile = build_empresa(params.country, rng)
                profiles.append(profile["empresa"])

        if params.count == 1:
            # Se apenas um, retorna direto (compatível com formato anterior)
            if params.kind == "pessoa":
                return OperationResult(meta={"pessoa": profiles[0]})
            else:
                return OperationResult(meta={"empresa": profiles[0]})
        else:
            # Se múltiplos, retorna lista
            return OperationResult(meta={params.kind + "s": profiles})
