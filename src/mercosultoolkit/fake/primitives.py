"""Geradores primitivos de um campo por vez para perfis fake."""

from __future__ import annotations

import random
import string
from collections.abc import Sequence
from datetime import datetime, timedelta

from mercosultoolkit.fake.data.base import CountryData


def pick_gender(rng: random.Random, data: CountryData) -> str:
    """Escolhe um gênero (masc/fem/não-binário)."""
    return rng.choice(data.genders)


def first_name(rng: random.Random, data: CountryData, gender: str) -> str:
    """Escolhe um nome próprio baseado no gênero."""
    if gender == "Feminino":
        return rng.choice(data.first_names_female)
    elif gender == "Não-binário":
        all_names = data.first_names_male + data.first_names_female
        return rng.choice(all_names)
    return rng.choice(data.first_names_male)


def surname(rng: random.Random, data: CountryData, count: int = 1) -> str:
    """Escolhe um ou mais sobrenomes e os junta."""
    surnames_list = [rng.choice(data.surnames) for _ in range(count)]
    return " ".join(surnames_list)


def full_name(
    rng: random.Random, data: CountryData, first: str | None = None, gender: str | None = None
) -> str:
    """Monta um nome completo (nome + sobrenome)."""
    if gender is None:
        gender = pick_gender(rng, data)
    if first is None:
        first = first_name(rng, data, gender)
    last = surname(rng, data, 1)
    return f"{first} {last}"


def email(rng: random.Random, data: CountryData, local_part: str) -> str:
    """Gera um endereço de e-mail."""
    domain = rng.choice(data.email_domains)
    clean_local = local_part.lower().replace(" ", ".").replace("á", "a").replace("é", "e")
    return f"{clean_local}@{domain}"


def corporate_email(rng: random.Random, company_domain: str, local_part: str) -> str:
    """Gera um e-mail corporativo a partir de um domínio."""
    clean_local = local_part.lower().replace(" ", ".").replace("á", "a").replace("é", "e")
    return f"{clean_local}@{company_domain}"


def phone_br(rng: random.Random, kind: str = "celular") -> str:
    """Gera um telefone brasileiro."""
    # DDD de 11 (São Paulo) para simplicidade
    ddd = rng.randint(11, 99)
    if kind == "celular":
        first_digit = rng.randint(9, 9)  # celular começa com 9
        rest = "".join(str(rng.randint(0, 9)) for _ in range(8))
        return f"+55 {ddd} 9{rest[:4]}-{rest[4:]}"
    else:
        first_digit = rng.randint(2, 8)
        rest = "".join(str(rng.randint(0, 9)) for _ in range(7))
        return f"+55 {ddd} {first_digit}{rest[:3]}-{rest[3:]}"


def cep_br(rng: random.Random) -> str:
    """Gera um CEP brasileiro válido em formato."""
    # CEP: 5 dígitos - 3 dígitos
    parte1 = "".join(str(rng.randint(0, 9)) for _ in range(5))
    parte2 = "".join(str(rng.randint(0, 9)) for _ in range(3))
    return f"{parte1}-{parte2}"


def birth_date(rng: random.Random, min_age: int = 18, max_age: int = 75) -> str:
    """Gera uma data de nascimento (ISO 8601)."""
    today = datetime.now()
    random_days = rng.randint(min_age * 365, max_age * 365)
    birth = today - timedelta(days=random_days)
    return birth.date().isoformat()


def age_from(birth_date_str: str) -> int:
    """Calcula a idade a partir de uma data de nascimento (ISO 8601)."""
    birth = datetime.fromisoformat(birth_date_str).date()
    today = datetime.now().date()
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age


def company_name(rng: random.Random, data: CountryData) -> tuple[str, str]:
    """Gera razão social e nome fantasia de uma empresa."""
    adj = rng.choice(data.street_names)
    noun = rng.choice(data.professions).title()
    company_type = rng.choice([data.company_types[-2:][0], data.company_types[-1]])
    razao_social = f"{adj} {noun} {company_type}"
    nome_fantasia = f"{adj} {noun}".replace(" ", " ")
    return razao_social, nome_fantasia


def company_domain(nome_fantasia: str) -> str:
    """Gera um domínio corporativo a partir do nome fantasia."""
    import unicodedata
    nfd = unicodedata.normalize("NFD", nome_fantasia)
    slug = "".join(c for c in nfd if unicodedata.category(c) != "Mn").lower().replace(" ", "")
    return f"{slug}.com.br"


def street_address(rng: random.Random, data: CountryData) -> dict[str, str]:
    """Gera um endereço de rua."""
    street_type = rng.choice(data.street_types)
    street_name = rng.choice(data.street_names)
    number = str(rng.randint(1, 9999))
    complement = ""
    if rng.random() > 0.5:
        complement = f"Apto {rng.randint(1, 300)}, Bloco {rng.choice(string.ascii_uppercase)}"

    state = rng.choice(data.states)
    city = rng.choice(data.cities_by_state.get(state, ["Desconhecida"]))
    neighborhood = rng.choice(data.neighborhoods)
    cep = cep_br(rng)

    return {
        "logradouro": f"{street_type} {street_name}",
        "numero": number,
        "complemento": complement,
        "bairro": neighborhood,
        "cidade": city,
        "estado": state,
        "cep": cep,
        "pais": "Brasil",
    }


def synthetic_inscricao_estadual(rng: random.Random) -> str:
    """Gera um número sintético de inscrição estadual (formato-only)."""
    return "".join(str(rng.randint(0, 9)) for _ in range(12))


def synthetic_inscricao_municipal(rng: random.Random) -> str:
    """Gera um número sintético de inscrição municipal (formato-only)."""
    return f"{rng.randint(1, 9999999)}-{rng.randint(0, 9)}"


def synthetic_bank_account(rng: random.Random) -> tuple[str, str]:
    """Gera agência e conta bancária sintética (sem DV real)."""
    agencia = f"{rng.randint(1000, 9999)}-{rng.randint(0, 9)}"
    conta = f"{rng.randint(100000, 999999)}-{rng.randint(0, 9)}"
    return agencia, conta


def money_amount(rng: random.Random, low: float = 1000, high: float = 100000) -> float:
    """Gera um valor monetário."""
    return round(rng.uniform(low, high), 2)


def height_cm(rng: random.Random, gender: str) -> int:
    """Gera uma altura plausível (em cm)."""
    if gender == "Feminino":
        return rng.randint(155, 175)
    elif gender == "Não-binário":
        return rng.randint(155, 185)
    return rng.randint(165, 185)


def weight_kg(rng: random.Random, height_cm: int) -> float:
    """Gera um peso plausível (em kg) baseado na altura."""
    # IMC alvo entre 18.5 e 28 (dentro da faixa normal/sobrepeso)
    height_m = height_cm / 100
    target_imc = rng.uniform(19, 27)
    weight = target_imc * (height_m ** 2)
    return round(weight, 1)


def maybe(rng: random.Random, probability: float = 0.5) -> bool:
    """Retorna True com uma dada probabilidade."""
    return rng.random() < probability


def pick_one(rng: random.Random, items: Sequence[str]) -> str:
    """Escolhe um item de uma sequência."""
    return rng.choice(items)


def pick_many(rng: random.Random, items: Sequence[str], count: int) -> list[str]:
    """Escolhe N itens distintos de uma sequência."""
    return rng.sample(items, min(count, len(items)))


def weighted_choice(rng: random.Random, weighted_items: list[tuple[str, int]]) -> str:
    """Escolhe um item de uma lista com pesos."""
    if not weighted_items:
        return ""
    items, weights = zip(*weighted_items)
    return rng.choices(list(items), weights=list(weights), k=1)[0]  # type: ignore[no-any-return]


def past_date(rng: random.Random, days_ago_min: int = 1, days_ago_max: int = 365) -> str:
    """Gera uma data no passado (ISO 8601)."""
    days = rng.randint(days_ago_min, days_ago_max)
    past = datetime.now() - timedelta(days=days)
    return past.date().isoformat()


def future_date(rng: random.Random, days_ahead_min: int = 1, days_ahead_max: int = 365) -> str:
    """Gera uma data no futuro (ISO 8601)."""
    days = rng.randint(days_ahead_min, days_ahead_max)
    future = datetime.now() + timedelta(days=days)
    return future.date().isoformat()
