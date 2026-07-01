"""Testes do catálogo de documentos."""

from __future__ import annotations

import pytest

from mercosultoolkit.core.errors import UnsupportedFormatError
from mercosultoolkit.documents.catalog import (
    all_documents,
    documents_by_country,
    get_document,
)


def test_get_document_by_name() -> None:
    """Verifica que get_document resolve documentos por nome."""
    # CPF já foi implementado
    doc = get_document("cpf")
    assert doc.name == "cpf"
    assert doc.country == "BR"


def test_aliases() -> None:
    """Verifica que aliases são resolvidos."""
    # Quando implementarmos os documentos, testar aliases como "run" -> "rut-cl"
    pass


def test_unknown_document_raises() -> None:
    """Verifica que documento desconhecido levanta UnsupportedFormatError."""
    with pytest.raises(UnsupportedFormatError, match="desconhecido"):
        get_document("xyz-invalid")


def test_all_documents_sorted() -> None:
    """Verifica que all_documents retorna ordenado."""
    docs = all_documents()
    names = [doc.name for doc in docs]
    assert names == sorted(names)


def test_documents_by_country() -> None:
    """Verifica filtro por país."""
    br_docs = documents_by_country("BR")
    for doc in br_docs:
        assert doc.country == "BR"

    ar_docs = documents_by_country("AR")
    for doc in ar_docs:
        assert doc.country == "AR"
