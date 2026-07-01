"""Modelo de um documento do catálogo.

Um :class:`DocumentScheme` casa metadados (país, família, padrão de máscara) com a lógica de
**gerar**, **parsear** (extrair metadados) e **validar** um valor. As operações genéricas
(generate/inspect/validate/mask/list-documents) consultam o catálogo por nome e delegam ao
esquema — elas não conhecem algoritmos individuais.

Documentos listados mas indisponíveis usam :class:`UnavailableDocument` e levantam
:class:`UnsupportedFormatError` em qualquer uso.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from mercosultoolkit.core.errors import InvalidInputError, UnsupportedFormatError


@dataclass(slots=True)
class GenContext:
    """Knobs de geração. Cada documento lê só o que lhe interessa; o resto é ignorado."""

    uf: str | None = None
    seed: int | None = None
    kind: str | None = None
    plate_format: str | None = None


def strip_mask(value: str) -> str:
    """Remove tudo que não é alfanumérico (mantém dígitos e letras, descarta . - / espaço)."""
    return "".join(ch for ch in value if ch.isalnum())


def apply_mask(raw: str, pattern: str) -> str:
    """Insere os literais de `pattern` nas posições fixas.

    `#` consome um caractere de `raw` (dígito); `@` consome um caractere alfanumérico
    (usado para placas e RUT-CL com 'K'); qualquer outro caractere do pattern é literal
    e não consome `raw`.

    Levanta InvalidInputError se o número de '#'/'@' em pattern != len(raw).
    """
    slot_count = sum(1 for ch in pattern if ch in "#@")
    if len(raw) != slot_count:
        raise InvalidInputError(
            f"padrão de máscara {pattern!r} exige {slot_count} caracteres, "
            f"recebeu {len(raw)}"
        )
    result = []
    raw_idx = 0
    for ch in pattern:
        if ch in "#@":
            result.append(raw[raw_idx])
            raw_idx += 1
        else:
            result.append(ch)
    return "".join(result)


class DocumentScheme(ABC):
    """Um esquema de documento: metadados + geração/parse/validação."""

    name: str
    country: str
    family: str
    summary: str
    mask: str | None = None
    available: bool = True
    reason: str = ""

    @abstractmethod
    def generate(self, ctx: GenContext) -> str:
        """Gera um novo documento deste esquema (válido estruturalmente), SEM máscara."""

    @abstractmethod
    def parse(self, value: str) -> dict[str, Any]:
        """Extrai metadados estruturados de ``value`` ou levanta :class:`InvalidInputError`.

        Remover máscara, validar dígitos verificadores, e retornar um dict com metadados
        extraídos.
        """

    def validate(self, value: str) -> bool:
        """Verdadeiro se ``value`` é um documento bem-formado deste esquema."""
        try:
            self.parse(value)
        except (InvalidInputError, ValueError):
            return False
        return True

    def apply_mask(self, value: str) -> str:
        """Aplica self.mask a um valor não-mascarado. Levanta se comprimento não casar."""
        if self.mask is None:
            return value
        return apply_mask(value, self.mask)

    def strip_mask_value(self, value: str) -> str:
        """Remove máscara de um valor."""
        return strip_mask(value)


class UnavailableDocument(DocumentScheme):
    """Documento listado mas indisponível: erra em qualquer uso, com motivo claro."""

    def __init__(
        self,
        name: str,
        country: str,
        family: str,
        summary: str,
        reason: str,
        mask: str | None = None,
    ) -> None:
        self.name = name
        self.country = country
        self.family = family
        self.summary = summary
        self.reason = reason
        self.available = False
        self.mask = mask

    def _raise(self) -> None:
        raise UnsupportedFormatError(f"documento {self.name!r} não suportado: {self.reason}")

    def generate(self, ctx: GenContext) -> str:
        self._raise()
        raise AssertionError  # pragma: no cover

    def parse(self, value: str) -> dict[str, Any]:
        self._raise()
        raise AssertionError  # pragma: no cover
