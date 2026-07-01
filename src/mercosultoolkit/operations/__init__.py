"""Operações genéricas sobre documentos.

Importar este módulo causa o auto-registro de todas as operações via decorador @register.
"""

from mercosultoolkit.operations import (  # noqa: F401
    generate,
    generate_profile,
    inspect,
    listing,
    mask,
    validate,
)
