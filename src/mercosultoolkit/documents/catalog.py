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
    "rg": "rg-br",
    "taxid-br": "cnpj",
    "cuil": "cuil-ar",
    "cuit": "cuit-ar",
    "ci-uy": "cedula-uy",
    "cedula": "cedula-uy",
    "pix": "pix-br",
    "titulo-eleitor": "titulo-eleitor-br",
    "cnh": "cnh-br",
    "passaporte": "passaporte-br",
}

# Documentos listados mas indisponíveis: (nome, país, família, resumo, motivo).
# Países além do BR ainda não têm algoritmos implementados; registrá-los aqui faz
# o nome resolver (alias incluso) e falhar com "não suportado" em vez de
# "desconhecido", além de aparecer no list-documents com o motivo.
_UNAVAILABLE: list[tuple[str, str, str, str, str]] = [
    ("dni-ar", "AR", "identificação", "DNI argentino", "ainda não implementado"),
    ("cuil-ar", "AR", "identificação", "CUIL argentino", "ainda não implementado"),
    ("cuit-ar", "AR", "identificação", "CUIT argentino", "ainda não implementado"),
    ("patente-ar", "AR", "veicular", "Patente argentina", "ainda não implementado"),
    ("cedula-uy", "UY", "identificação", "Cédula uruguaia", "ainda não implementado"),
    ("rut-uy", "UY", "identificação", "RUT uruguaio", "ainda não implementado"),
    ("matricula-uy", "UY", "identificação", "Matrícula uruguaia", "ainda não implementado"),
    ("cedula-py", "PY", "identificação", "Cédula paraguaia", "ainda não implementado"),
    ("ruc-py", "PY", "identificação", "RUC paraguaio", "ainda não implementado"),
    ("rut-cl", "CL", "identificação", "RUT/RUN chileno", "ainda não implementado"),
    ("patente-cl", "CL", "veicular", "Patente chilena", "ainda não implementado"),
]


@cache
def _registry() -> dict[str, DocumentScheme]:
    docs: list[DocumentScheme] = []
    for module in (br, ar, uy, py, cl):
        docs.extend(module.build())
    registry = {doc.name: doc for doc in docs}
    for name, country, family, summary, reason in _UNAVAILABLE:
        # setdefault: implementação real futura de mesmo nome vence o placeholder
        registry.setdefault(name, UnavailableDocument(name, country, family, summary, reason))
    return registry


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


def document_names() -> list[str]:
    """Nomes canônicos dos documentos utilizáveis, ordenados.

    Alimenta o ``enum`` do JSON Schema das operações — o hub genérico do site
    transforma esse enum em dropdown, então nomes inválidos nem chegam à API.
    """
    return [doc.name for doc in available_documents()]


def documents_by_country(country: str) -> list[DocumentScheme]:
    """Documentos de um país específico, ordenados por nome."""
    country_upper = country.upper()
    return [doc for doc in all_documents() if doc.country == country_upper]
