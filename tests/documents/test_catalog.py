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
    assert get_document("rg").name == "rg-br"
    assert get_document("cnh").name == "cnh-br"
    assert get_document("pix").name == "pix-br"


def test_unavailable_document_has_clear_reason() -> None:
    """Documento de país não implementado resolve, mas falha com motivo claro.

    Regressão: 'cuil-ar' (e o alias 'cuil') devolviam "documento desconhecido"
    porque a Argentina não tem implementação — hoje o nome resolve para um
    placeholder indisponível.
    """
    doc = get_document("cuil-ar")
    assert doc.available is False
    assert doc.name == "cuil-ar"
    assert doc.country == "AR"
    with pytest.raises(UnsupportedFormatError, match="não suportado"):
        doc.parse("20-12345678-9")


def test_unknown_document_raises() -> None:
    """Verifica que documento desconhecido levanta UnsupportedFormatError."""
    with pytest.raises(UnsupportedFormatError, match="desconhecido"):
        get_document("xyz-invalid")


def test_document_names_excludes_unavailable() -> None:
    """O enum de nomes publicado no schema só contém documentos utilizáveis."""
    from mercosultoolkit.documents.catalog import document_names

    names = document_names()
    assert "cpf" in names
    assert "rg-br" in names
    assert "cuil-ar" not in names
    assert names == sorted(names)


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
