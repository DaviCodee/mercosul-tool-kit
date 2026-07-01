"""Composição de perfis fake de pessoa e empresa."""

from __future__ import annotations

import random
from typing import Any

from mercosultoolkit.documents.base import GenContext, rng_for
from mercosultoolkit.documents.catalog import get_document
from mercosultoolkit.fake.data import get_country_data
from mercosultoolkit.fake import primitives


def build_pessoa(country: str, rng: random.Random) -> dict[str, Any]:
    """Gera um perfil completo de pessoa fake."""
    data = get_country_data(country)

    # Gênero e nomes
    gender = primitives.pick_gender(rng, data)
    first = primitives.first_name(rng, data, gender)
    last = primitives.surname(rng, data, 1)
    full_name = f"{first} {last}"

    # Data de nascimento e idade
    birth_date_str = primitives.birth_date(rng, min_age=18, max_age=75)
    age = primitives.age_from(birth_date_str)

    # Características físicas
    height = primitives.height_cm(rng, gender)
    weight = primitives.weight_kg(rng, height)

    # Contato
    email_personal = primitives.email(rng, data, full_name)
    phone = primitives.phone_br(rng, "celular")

    # Endereço
    address = primitives.street_address(rng, data)

    # Profissional
    job_title = primitives.pick_one(rng, data.job_titles)
    profession = primitives.pick_one(rng, data.professions)

    # Educação
    education_level = primitives.pick_one(rng, data.education_levels)
    university_course = primitives.pick_one(rng, data.courses)

    # Saúde
    blood_type = primitives.weighted_choice(rng, data.blood_types)
    allergies = primitives.pick_many(rng, data.allergies, rng.randint(0, 3))
    medications = primitives.pick_many(rng, data.medications, rng.randint(0, 2))

    # Preferências
    hobbies = primitives.pick_many(rng, data.hobbies, rng.randint(1, 4))
    languages = primitives.pick_many(rng, data.languages, rng.randint(1, 4))

    # Estado civil
    marital_status = primitives.pick_one(rng, data.marital_statuses)

    # Documentos reais: cada um recebe um sub-seed garantindo determinismo sem repetição
    cpf_ctx = GenContext(seed=rng.randint(0, 2**31 - 1))
    cpf_doc = get_document("cpf")
    cpf_raw = cpf_doc.generate(cpf_ctx)
    cpf_masked = cpf_doc.apply_mask(cpf_raw)

    rg_ctx = GenContext(seed=rng.randint(0, 2**31 - 1), uf=address["estado"])
    rg_doc = get_document("rg-br")
    rg_raw = rg_doc.generate(rg_ctx)
    rg_masked = rg_doc.apply_mask(rg_raw)

    titulo_ctx = GenContext(seed=rng.randint(0, 2**31 - 1), uf=address["estado"])
    titulo_doc = get_document("titulo-eleitor-br")
    titulo_raw = titulo_doc.generate(titulo_ctx)
    titulo_masked = titulo_doc.apply_mask(titulo_raw)

    cnh_ctx = GenContext(seed=rng.randint(0, 2**31 - 1))
    cnh_doc = get_document("cnh-br")
    cnh_raw = cnh_doc.generate(cnh_ctx)
    cnh_masked = cnh_doc.apply_mask(cnh_raw)

    passaporte_ctx = GenContext(seed=rng.randint(0, 2**31 - 1))
    passaporte_doc = get_document("passaporte-br")
    passaporte_raw = passaporte_doc.generate(passaporte_ctx)
    passaporte_masked = passaporte_doc.apply_mask(passaporte_raw)

    # Dados bancários sintéticos
    agencia, conta = primitives.synthetic_bank_account(rng)
    banco_code, banco_name = rng.choice(data.banks)

    # Certificações
    certifications = primitives.pick_many(rng, data.certifications, rng.randint(0, 2))

    # Outros
    naturalidade = {
        "cidade": address["cidade"],
        "estado": address["estado"],
        "pais": "Brasil",
    }

    return {
        "pessoa": {
            "identificacao": {
                "nome_completo": full_name,
                "nome_proprio": first,
                "sobrenome": last,
                "genero": gender,
                "data_nascimento": birth_date_str,
                "idade_anos": age,
                "naturalidade": naturalidade,
            },
            "documentos_e_registros": {
                "cpf": cpf_masked,
                "rg": {
                    "numero": rg_masked,
                    "estado_emissor": address["estado"],
                },
                "titulo_eleitor": titulo_masked,
                "cnh": {
                    "numero": cnh_masked,
                    "categorias": primitives.pick_many(rng, data.cnh_categories, rng.randint(1, 3)),
                },
                "passaporte": passaporte_masked,
            },
            "caracteristicas_fisicas": {
                "altura_cm": height,
                "peso_kg": weight,
                "tipo_sanguineo": blood_type,
            },
            "saude": {
                "alergias": allergies,
                "medicamentos_em_uso": medications,
            },
            "contato": {
                "email_pessoal": email_personal,
                "telefone_celular": phone,
                "endereco_residencial": {
                    "logradouro": address["logradouro"],
                    "numero": address["numero"],
                    "complemento": address["complemento"],
                    "bairro": address["bairro"],
                    "cidade": address["cidade"],
                    "estado": address["estado"],
                    "cep": address["cep"],
                    "pais": address["pais"],
                },
            },
            "profissional": {
                "cargo_atual": job_title,
                "profissao": profession,
                "email_trabalho": None,  # preenchido se houver empresa_atual
            },
            "educacao": {
                "nivel_escolaridade": education_level,
                "curso_universitario": university_course,
                "certifications": certifications,
            },
            "dados_bancarios": {
                "banco_principal": {
                    "codigo": banco_code,
                    "nome": banco_name,
                },
                "agencia": agencia,
                "conta": conta,
            },
            "preferencias": {
                "hobbies": hobbies,
                "idiomas": languages,
            },
            "estado_civil": marital_status,
        }
    }


def build_empresa(country: str, rng: random.Random) -> dict[str, Any]:
    """Gera um perfil completo de empresa fake."""
    data = get_country_data(country)

    # Razão social e nome fantasia
    razao_social, nome_fantasia = primitives.company_name(rng, data)
    domain = primitives.company_domain(nome_fantasia)

    # Endereço
    address = primitives.street_address(rng, data)

    # Tipo, porte, situação cadastral
    company_type = primitives.pick_one(rng, data.company_types)
    company_size = primitives.pick_one(rng, data.company_sizes)
    cadastral_status = primitives.weighted_choice(rng, data.cadastral_statuses)
    tax_regime = primitives.pick_one(rng, data.tax_regimes)
    revenue_bracket = primitives.pick_one(rng, data.revenue_brackets)

    # Data de fundação
    founded_date = primitives.past_date(rng, days_ago_min=365, days_ago_max=20*365)
    years_in_business = primitives.age_from(founded_date)

    # Contato
    email_corporate = primitives.corporate_email(rng, domain, "contato")
    phone = primitives.phone_br(rng, "fixo")

    # Documentos reais
    cnpj_ctx = GenContext(seed=rng.randint(0, 2**31 - 1))
    cnpj_doc = get_document("cnpj")
    cnpj_raw = cnpj_doc.generate(cnpj_ctx)
    cnpj_masked = cnpj_doc.apply_mask(cnpj_raw)

    # Inscrições sintéticas (sem DV real)
    inscricao_estadual = primitives.synthetic_inscricao_estadual(rng)
    inscricao_municipal = primitives.synthetic_inscricao_municipal(rng)

    # CNAE
    cnae_code, cnae_description = rng.choice(data.cnaes)

    # Dados bancários
    agencia, conta = primitives.synthetic_bank_account(rng)
    banco_code, banco_name = rng.choice(data.banks)

    # Pix: reutiliza o mesmo CNPJ da empresa (não gera um novo)
    pix_ctx = GenContext(seed=rng.randint(0, 2**31 - 1), kind="cnpj")
    pix_doc = get_document("pix-br")
    pix_raw = cnpj_raw  # reutiliza o CNPJ da empresa
    pix_masked = pix_doc.apply_mask(pix_raw)

    # Certificações e selos
    certifications = primitives.pick_many(rng, data.certifications, rng.randint(0, 3))
    sustainability_seals = primitives.pick_many(rng, data.sustainability_seals, rng.randint(0, 2))

    # Funcionários simulados
    num_employees_ranges = {
        "MEI": (1, 1),
        "Micro": (2, 9),
        "Pequena": (10, 49),
        "Média": (50, 249),
        "Grande": (250, 5000),
    }
    min_emp, max_emp = num_employees_ranges.get(company_size, (1, 100))
    num_employees = rng.randint(min_emp, max_emp)

    return {
        "empresa": {
            "identificacao": {
                "razao_social": razao_social,
                "nome_fantasia": nome_fantasia,
                "site": f"https://www.{domain}",
                "data_fundacao": founded_date,
                "anos_em_funcionamento": years_in_business,
            },
            "documentos_e_registros": {
                "cnpj": cnpj_masked,
                "inscricao_estadual": inscricao_estadual,
                "inscricao_municipal": inscricao_municipal,
            },
            "classificacao": {
                "tipo_empresa": company_type,
                "porte": company_size,
                "situacao_cadastral": cadastral_status,
                "regime_tributario": tax_regime,
                "faixa_faturamento_anual": revenue_bracket,
            },
            "atividade_economica": {
                "cnae_principal": {
                    "codigo": cnae_code,
                    "descricao": cnae_description,
                },
            },
            "endereco_comercial": {
                "logradouro": address["logradouro"],
                "numero": address["numero"],
                "complemento": address["complemento"],
                "bairro": address["bairro"],
                "cidade": address["cidade"],
                "estado": address["estado"],
                "cep": address["cep"],
                "pais": address["pais"],
            },
            "contato": {
                "email": email_corporate,
                "telefone": phone,
                "dominio_internet": domain,
            },
            "financeiro_patrimonial": {
                "dados_bancarios_principais": {
                    "banco": {
                        "codigo": banco_code,
                        "nome": banco_name,
                    },
                    "agencia": agencia,
                    "conta": conta,
                    "chave_pix_principal": cnpj_masked,  # CRÍTICO: reutiliza CNPJ
                },
            },
            "recursos_humanos": {
                "numero_funcionarios": num_employees,
            },
            "certificacoes_e_selos": {
                "certificacoes": certifications,
                "selos_sustentabilidade": sustainability_seals,
            },
        }
    }
