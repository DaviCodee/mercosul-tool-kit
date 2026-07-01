"""Definição da estrutura de dados para cada país no gerador fake."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CountryData:
    """Pool de dados curados para gerar perfis fake de uma região."""

    country: str

    # Nomes
    first_names_male: list[str] = field(default_factory=list)
    first_names_female: list[str] = field(default_factory=list)
    surnames: list[str] = field(default_factory=list)

    # Geografia
    cities_by_state: dict[str, list[str]] = field(default_factory=dict)
    states: list[str] = field(default_factory=list)

    # Documentos e financeiro
    banks: list[tuple[str, str]] = field(default_factory=list)  # (código, nome)
    cnaes: list[tuple[str, str]] = field(default_factory=list)  # (código, descrição)

    # Profissional
    email_domains: list[str] = field(default_factory=list)
    street_types: list[str] = field(default_factory=list)
    street_names: list[str] = field(default_factory=list)
    neighborhoods: list[str] = field(default_factory=list)
    job_titles: list[str] = field(default_factory=list)
    professions: list[str] = field(default_factory=list)
    courses: list[str] = field(default_factory=list)

    # Saúde
    blood_types: list[tuple[str, int]] = field(default_factory=list)  # (tipo, peso)
    allergies: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)

    # Preferências
    hobbies: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    sustainability_seals: list[str] = field(default_factory=list)

    # Empresa
    company_types: list[str] = field(default_factory=list)
    company_sizes: list[str] = field(default_factory=list)
    cadastral_statuses: list[tuple[str, int]] = field(default_factory=list)  # (status, peso)
    tax_regimes: list[str] = field(default_factory=list)
    revenue_brackets: list[str] = field(default_factory=list)

    # Pessoa
    marital_statuses: list[str] = field(default_factory=list)
    education_levels: list[str] = field(default_factory=list)
    genders: list[str] = field(default_factory=list)
    cnh_categories: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)
