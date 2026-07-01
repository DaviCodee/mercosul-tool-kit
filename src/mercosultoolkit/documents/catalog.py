"""Catálogo de documentos: monta o registro e resolve nomes/aliases.

Há dois registros no toolkit: o de operações (``core/registry.py``) e este, o de
*documentos*. As operações genéricas (generate/inspect/validate/mask/list-documents)
consultam ``get_document`` por nome.

Documentos efetivamente suportados vêm dos módulos de cada país (br, ar, uy, py, cl).
Itens que não têm algoritmo público (ex.: cédula paraguaia) ficam **listados mas
indisponíveis**, com motivo claro.
"""

from __future__ import annotations

from functools import cache

from mercosultoolkit.core.errors import UnsupportedFormatError
from mercosultoolkit.documents import ar, br, cl, py, uy
from mercosultoolkit.documents.base import DocumentScheme, UnavailableDocument

# Aliases convenientes (entrada do usuário -> nome canônico).
_ALIASES = {
    "run": "rut-cl",
    "rut": "rut-cl",
    "taxid-br": "cnpj",
    "cuil": "cuil-ar",
    "cuit": "cuit-ar",
    "ci-uy": "cedula-uy",
    "cedula": "cedula-uy",
    "pix": "pix-br",
    "titulo-eleitor": "titulo-eleitor-br",
}

# Documentos listados mas indisponíveis: (nome, país, família, resumo, motivo).
_UNAVAILABLE: list[tuple[str, str, str, str, str]] = []


@cache
def _registry() -> dict[str, DocumentScheme]:
    docs: list[DocumentScheme] = []
    for module in (br, ar, uy, py, cl):
        docs.extend(module.build())
    for name, country, family, summary, reason in _UNAVAILABLE:
        docs.append(UnavailableDocument(name, country, family, summary, reason))
    return {doc.name: doc for doc in docs}


def get_document(name: str) -> DocumentScheme:
    """Resolve ``name`` (com aliases) para documento ou levanta UnsupportedFormatError."""
    key = name.strip().lower()
    key = _ALIASES.get(key, key)
    registry = _registry()
    try:
        return registry[key]
    except KeyError:
        raise UnsupportedFormatError(f"documento desconhecido: {name!r}") from None


def all_documents() -> list[DocumentScheme]:
    """Todos os documentos do catálogo, ordenados por nome."""
    registry = _registry()
    return [registry[name] for name in sorted(registry)]


def available_documents() -> list[DocumentScheme]:
    """Apenas os documentos utilizáveis (exclui os indisponíveis)."""
    return [doc for doc in all_documents() if doc.available]


def documents_by_country(country: str) -> list[DocumentScheme]:
    """Documentos de um país específico, ordenados por nome."""
    country_upper = country.upper()
    return [doc for doc in all_documents() if doc.country == country_upper]
