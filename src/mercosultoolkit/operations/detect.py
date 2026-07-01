"""Detecção heurística do tipo de um documento.

A identificação é inerentemente ambígua (várias strings curtas satisfazem vários
documentos), então tentamos os documentos mais estruturados primeiro e devolvemos tanto o
melhor palpite quanto a lista completa de candidatos.
"""

from __future__ import annotations

from mercosultoolkit.documents.catalog import get_document

# Ordem de prioridade: do mais restrito/estruturado para o mais permissivo.
# Documentos com comprimento fixo e DV bem definido vêm primeiro.
DETECT_ORDER = (
    "cnpj",           # 14 dígitos, muito específico
    "titulo-eleitor-br",  # 12 dígitos
    "cns",            # 15 dígitos, conjunto de dígitos iniciais restrito
    "cuil-ar",        # 11 dígitos + DV
    "cuit-ar",        # 11 dígitos + DV (prefixos diferentes de CUIL)
    "pis",            # 11 dígitos + DV
    "ruc-py",         # variável, forma jurídica é 8+1
    "rut-uy",         # 12 dígitos (forma jurídica) ou CI+001
    "cpf",            # 11 dígitos + DV
    "rut-cl",         # 7-9 dígitos + DV (incl. K)
    "cedula-uy",      # 7 dígitos + DV
    "renavam",        # 11 dígitos + DV
    "dni-ar",         # 7-8 dígitos, sem DV (mais permissivo)
    "cedula-py",      # formato-apenas, bem permissivo
    "rg-br",          # formato-apenas, permissivo
    # Placas/veicular: formato-apenas, baixo risco de colisão com IDs numéricos
    "placa-br",
    "placa-py",
    "patente-ar",
    "patente-cl",
    "matricula-uy",
    # Pix: despacha para CPF/CNPJ/email/phone/UUID — vem por último já que é um superset
    "pix-br",
)


def detect(value: str) -> list[str]:
    """Nomes dos documentos que consideram ``value`` válido, em ordem de prioridade."""
    return [name for name in DETECT_ORDER if get_document(name).validate(value)]
