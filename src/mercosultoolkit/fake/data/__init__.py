"""Registro de dados por país para o gerador fake."""

from __future__ import annotations

from mercosultoolkit.core.errors import InvalidInputError
from mercosultoolkit.fake.data.base import CountryData
from mercosultoolkit.fake.data import br

_REGISTRY = {
    "BR": br.DATA,
}


def get_country_data(country: str) -> CountryData:
    """Retorna os pools de dados curados para um país."""
    key = country.upper()
    if key not in _REGISTRY:
        raise InvalidInputError(
            f"país {country!r} não suportado (disponível: BR)"
        )
    return _REGISTRY[key]
