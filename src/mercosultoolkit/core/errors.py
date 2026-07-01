"""Hierarquia de erros do toolkit.

Os adaptadores traduzem essas exceções em códigos de saída (CLI) ou status HTTP (API).
"""

from __future__ import annotations


class MercosulToolkitError(Exception):
    """Raiz de todos os erros tratáveis do toolkit."""


class InvalidInputError(MercosulToolkitError):
    """Entrada inválida: valor mal-formado, parâmetro ausente ou fora de faixa…"""


class UnsupportedFormatError(InvalidInputError):
    """Documento solicitado não é suportado por este toolkit (ou nem existe)."""


class OperationError(MercosulToolkitError):
    """Falha durante a execução de uma operação."""


class MissingDependencyError(MercosulToolkitError):
    """Funcionalidade requer uma dependência/binário opcional não instalado."""
