"""Documentos brasileiros: CPF, CNPJ, RG, CNS, PIS, Título de Eleitor, RENAVAM, Placa, Pix, CNH, Passaporte."""

from __future__ import annotations

from typing import Any

from mercosultoolkit.core.errors import InvalidInputError
from mercosultoolkit.documents.base import DocumentScheme, GenContext, rng_for, strip_mask


def _mod11_dv_standard(digits: str, weights: list[int], mod11_special: bool = False) -> str:
    """Calcula DV mod-11 padrão: soma ponderada, resto, DV = (11 - resto) % 11.

    Se mod11_special=True, trata resto < 2 como DV=0 (regra do CNPJ).
    """
    if len(digits) != len(weights):
        raise ValueError(f"Quantidade de dígitos ({len(digits)}) != pesos ({len(weights)})")
    soma = sum(int(d) * w for d, w in zip(digits, weights))
    resto = soma % 11
    if mod11_special and resto < 2:
        dv = 0
    else:
        dv = (11 - resto) % 11
    return str(dv)


def _char_value(ch: str) -> int:
    """Valor de um caractere para CNPJ alfanumérico: ord(ch) - 48."""
    return ord(ch) - 48


class CPF(DocumentScheme):
    name = "cpf"
    country = "BR"
    family = "identificação"
    summary = "CPF: Cadastro de Pessoa Física (11 dígitos + 2 DVs)"
    mask = "###.###.###-##"

    def generate(self, ctx: GenContext) -> str:
        rng = rng_for(ctx)
        while True:
            base = "".join(str(rng.randint(0, 9)) for _ in range(9))
            if len(set(base)) > 1:  # rejeita sequências de dígito único (ex: 000000000)
                break

        dv1 = _mod11_dv_standard(base, [10, 9, 8, 7, 6, 5, 4, 3, 2], mod11_special=True)
        dv2 = _mod11_dv_standard(base + dv1, [11, 10, 9, 8, 7, 6, 5, 4, 3, 2], mod11_special=True)
        return base + dv1 + dv2

    def parse(self, value: str) -> dict[str, Any]:
        raw = strip_mask(value)
        if len(raw) != 11 or not raw.isdigit():
            raise InvalidInputError(f"CPF deve ter 11 dígitos, recebeu {len(raw)}")

        base = raw[:9]
        dv1_received = raw[9]
        dv2_received = raw[10]

        if len(set(base)) == 1:
            raise InvalidInputError("CPF com sequência de dígito único inválida")

        dv1_expected = _mod11_dv_standard(base, [10, 9, 8, 7, 6, 5, 4, 3, 2], mod11_special=True)
        if dv1_received != dv1_expected:
            raise InvalidInputError(f"CPF: DV1 inválida (esperado {dv1_expected}, recebeu {dv1_received})")

        dv2_expected = _mod11_dv_standard(base + dv1_received, [11, 10, 9, 8, 7, 6, 5, 4, 3, 2], mod11_special=True)
        if dv2_received != dv2_expected:
            raise InvalidInputError(f"CPF: DV2 inválida (esperado {dv2_expected}, recebeu {dv2_received})")

        return {"cpf": raw}


class CNPJ(DocumentScheme):
    name = "cnpj"
    country = "BR"
    family = "identificação"
    summary = "CNPJ: Cadastro Nacional da Pessoa Jurídica (numérico 14 dígitos ou alfanumérico)"
    mask = "##.###.###/####-##"

    def generate(self, ctx: GenContext) -> str:
        rng = rng_for(ctx)
        # TODO: Implementar CNPJ alfanumérico (2026+) com algoritmo completo
        # Por enquanto, gera apenas numérico
        base = "".join(str(rng.randint(0, 9)) for _ in range(12))
        dv1 = _mod11_dv_standard(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2], mod11_special=True)
        dv2 = _mod11_dv_standard(base + dv1, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2], mod11_special=True)
        return base + dv1 + dv2

    def parse(self, value: str) -> dict[str, Any]:
        raw = strip_mask(value)

        if len(raw) == 14 and raw.isdigit():
            base = raw[:12]
            dv1_received = raw[12]
            dv2_received = raw[13]

            dv1_expected = _mod11_dv_standard(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2], mod11_special=True)
            if dv1_received != dv1_expected:
                raise InvalidInputError(f"CNPJ: DV1 inválida")

            dv2_expected = _mod11_dv_standard(base + dv1_received, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2], mod11_special=True)
            if dv2_received != dv2_expected:
                raise InvalidInputError(f"CNPJ: DV2 inválida")

            return {"cnpj": raw, "kind": "numerico"}
        else:
            raise InvalidInputError(f"CNPJ deve ter 14 dígitos, recebeu {len(raw)}")

    def apply_mask(self, value: str) -> str:
        """Aplica máscara compatível com o tipo de CNPJ."""
        if not value[:12].isdigit():
            return value  # alfanumérico: sem máscara
        return super().apply_mask(value)


class RG(DocumentScheme):
    name = "rg-br"
    country = "BR"
    family = "identificação"
    summary = "RG: Registro Geral (formato apenas, sem checksum nacional)"
    mask = "########-#"
    available = True

    def generate(self, ctx: GenContext) -> str:
        rng = rng_for(ctx)
        return "".join(str(rng.randint(0, 9)) for _ in range(9))

    def parse(self, value: str) -> dict[str, Any]:
        raw = strip_mask(value)
        if len(raw) < 8 or len(raw) > 9:
            raise InvalidInputError(f"RG deve ter 8-9 dígitos, recebeu {len(raw)}")
        if not raw[:-1].isdigit() or not (raw[-1].isdigit() or raw[-1] == 'X'):
            raise InvalidInputError("RG deve ser numérico + X opcional no final")
        return {"rg": raw}


class CNS(DocumentScheme):
    name = "cns"
    country = "BR"
    family = "saúde"
    summary = "CNS: Cartão Nacional de Saúde (15 dígitos: definitivo ou provisório)"
    mask = "#############"

    def generate(self, ctx: GenContext) -> str:
        rng = rng_for(ctx)
        if ctx.kind == "provisorio":
            first_digit = rng.choice([7, 8, 9])
            rest = "".join(str(rng.randint(0, 9)) for _ in range(14))
            return f"{first_digit}{rest}"
        else:
            base_11 = "".join(str(rng.randint(0, 9)) for _ in range(11))
            soma = sum(int(d) * w for d, w in zip(base_11, [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5]))
            dv = 11 - (soma % 11)
            if dv == 10:
                dv = 0
            elif dv == 11:
                dv = 0
            resto_3 = "".join(str(rng.randint(0, 9)) for _ in range(3))
            return f"1{base_11}{dv}{resto_3}"

    def parse(self, value: str) -> dict[str, Any]:
        raw = strip_mask(value)
        if len(raw) != 15 or not raw.isdigit():
            raise InvalidInputError(f"CNS deve ter 15 dígitos, recebeu {len(raw)}")

        first = int(raw[0])
        if first in [7, 8, 9]:
            soma = sum(int(d) for d in raw)
            if soma % 11 != 0:
                raise InvalidInputError("CNS provisório: checksum inválido")
        elif first == 1:
            base_11 = raw[1:12]
            dv_received = int(raw[12])
            soma = sum(int(d) * w for d, w in zip(base_11, [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5]))
            dv_expected = 11 - (soma % 11)
            if dv_expected >= 10:
                dv_expected = 0
            if dv_received != dv_expected:
                raise InvalidInputError(f"CNS definitivo: DV inválida")
        else:
            raise InvalidInputError("CNS deve começar com 1, 7, 8 ou 9")

        return {"cns": raw}


class PIS(DocumentScheme):
    name = "pis"
    country = "BR"
    family = "identificação"
    summary = "PIS: Programa de Integração Social (11 dígitos)"
    mask = "###.###.##-##"

    def generate(self, ctx: GenContext) -> str:
        rng = rng_for(ctx)
        base = "".join(str(rng.randint(0, 9)) for _ in range(10))
        dv = _mod11_dv_standard(base, [3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
        return base + dv

    def parse(self, value: str) -> dict[str, Any]:
        raw = strip_mask(value)
        if len(raw) != 11 or not raw.isdigit():
            raise InvalidInputError(f"PIS deve ter 11 dígitos, recebeu {len(raw)}")

        base = raw[:10]
        dv_received = raw[10]
        dv_expected = _mod11_dv_standard(base, [3, 2, 9, 8, 7, 6, 5, 4, 3, 2])

        if dv_received != dv_expected:
            raise InvalidInputError(f"PIS: DV inválida (esperado {dv_expected}, recebeu {dv_received})")

        return {"pis": raw}


class TituloEleitor(DocumentScheme):
    name = "titulo-eleitor-br"
    country = "BR"
    family = "identificação"
    summary = "Título de Eleitor: 8 dígitos sequencial + UF + 2 DVs"
    mask = "######## ## ##"

    _UF_CODES = {
        "AC": 4, "AL": 17, "AP": 16, "AM": 3, "BA": 5, "CE": 7, "DF": 26, "ES": 14,
        "GO": 10, "MA": 11, "MT": 28, "MS": 10, "MG": 31, "PA": 13, "PB": 12, "PR": 22,
        "PE": 8, "PI": 15, "RJ": 6, "RN": 20, "RS": 4, "RO": 23, "RR": 24, "SC": 24,
        "SP": 1, "SE": 25, "TO": 27,
    }

    def generate(self, ctx: GenContext) -> str:
        rng = rng_for(ctx)
        sequencial = "".join(str(rng.randint(0, 9)) for _ in range(8))
        uf = ctx.uf or "SP"

        uf_code = self._UF_CODES.get(uf, 1)
        estado_str = str(uf_code).zfill(2)

        dv1_base = sequencial
        dv1_soma = sum(int(d) * w for d, w in zip(dv1_base, [2, 3, 4, 5, 6, 7, 8, 9]))
        dv1_resto = dv1_soma % 11
        if dv1_resto < 2:
            dv1 = 0
        else:
            dv1 = 11 - dv1_resto

        dv2_base = estado_str + str(dv1)
        dv2_soma = sum(int(d) * w for d, w in zip(dv2_base, [7, 8, 9]))
        dv2_resto = dv2_soma % 11
        if dv2_resto >= 10:
            dv2 = 0
        else:
            dv2 = dv2_resto

        return sequencial + estado_str + str(dv1) + str(dv2)

    def parse(self, value: str) -> dict[str, Any]:
        raw = strip_mask(value)
        if len(raw) != 12 or not raw.isdigit():
            raise InvalidInputError(f"Título de Eleitor deve ter 12 dígitos, recebeu {len(raw)}")

        sequencial = raw[:8]
        estado_code = raw[8:10]
        dv1_received = int(raw[10])
        dv2_received = int(raw[11])

        dv1_soma = sum(int(d) * w for d, w in zip(sequencial, [2, 3, 4, 5, 6, 7, 8, 9]))
        dv1_resto = dv1_soma % 11
        if dv1_resto < 2:
            dv1_expected = 0
        else:
            dv1_expected = 11 - dv1_resto

        if dv1_received != dv1_expected:
            raise InvalidInputError(f"Título: DV1 inválida")

        dv2_soma = sum(int(d) * w for d, w in zip(estado_code + str(dv1_received), [7, 8, 9]))
        dv2_resto = dv2_soma % 11
        if dv2_resto >= 10:
            dv2_expected = 0
        else:
            dv2_expected = dv2_resto
        if dv2_received != dv2_expected:
            raise InvalidInputError(f"Título: DV2 inválida")

        uf = next((k for k, v in self._UF_CODES.items() if str(v).zfill(2) == estado_code), None)
        return {"titulo_eleitor": raw, "uf": uf}


class RENAVAM(DocumentScheme):
    name = "renavam"
    country = "BR"
    family = "veicular"
    summary = "RENAVAM: Registro Nacional de Automóvel em Vias (10 dígitos)"
    mask = "##.###.###-##"

    def generate(self, ctx: GenContext) -> str:
        rng = rng_for(ctx)
        base = "".join(str(rng.randint(0, 9)) for _ in range(9))
        soma = sum(int(d) * w for d, w in zip(base, [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]))
        dv = (soma * 10) % 11
        if dv == 10:
            dv = 0
        return base + str(dv)

    def parse(self, value: str) -> dict[str, Any]:
        raw = strip_mask(value)
        if len(raw) != 10 or not raw.isdigit():
            raise InvalidInputError(f"RENAVAM deve ter 10 dígitos, recebeu {len(raw)}")

        base = raw[:9]
        dv_received = int(raw[9])
        soma = sum(int(d) * w for d, w in zip(base, [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]))
        dv_expected = (soma * 10) % 11
        if dv_expected == 10:
            dv_expected = 0

        if dv_received != dv_expected:
            raise InvalidInputError(f"RENAVAM: DV inválida (esperado {dv_expected}, recebeu {dv_received})")

        return {"renavam": raw}


class Placa(DocumentScheme):
    name = "placa-br"
    country = "BR"
    family = "veicular"
    summary = "Placa veicular: LLL-9999 (old) ou LLL9L99 (Mercosul)"
    mask = None

    def generate(self, ctx: GenContext) -> str:
        rng = rng_for(ctx)
        letras = "".join(chr(rng.randint(65, 90)) for _ in range(3))

        if ctx.plate_format == "old":
            numeros = "".join(str(rng.randint(0, 9)) for _ in range(4))
            return f"{letras}{numeros}"
        else:
            num1 = str(rng.randint(0, 9))
            letra = chr(rng.randint(65, 90))
            num2 = "".join(str(rng.randint(0, 9)) for _ in range(2))
            return f"{letras}{num1}{letra}{num2}"

    def parse(self, value: str) -> dict[str, Any]:
        raw = value.upper().replace("-", "").replace(" ", "")

        if len(raw) == 7 and raw[:3].isalpha() and raw[3:].isdigit():
            return {"placa": raw, "formato": "antigo"}
        elif len(raw) == 7 and raw[:3].isalpha() and raw[3].isdigit() and raw[4].isalpha() and raw[5:].isdigit():
            return {"placa": raw, "formato": "mercosul"}
        else:
            raise InvalidInputError(f"Placa inválida: {value}")

    def apply_mask(self, value: str) -> str:
        if len(value) == 7 and value[:3].isalpha() and value[3:].isdigit():
            return f"{value[:3]}-{value[3:]}"
        return value


class Passaporte(DocumentScheme):
    name = "passaporte-br"
    country = "BR"
    family = "identificação"
    summary = "Passaporte: 2 letras + 6 dígitos (formato apenas)"
    mask = "@@######"

    def generate(self, ctx: GenContext) -> str:
        rng = rng_for(ctx)
        letras = "".join(chr(rng.randint(65, 90)) for _ in range(2))
        numeros = "".join(str(rng.randint(0, 9)) for _ in range(6))
        return f"{letras}{numeros}"

    def parse(self, value: str) -> dict[str, Any]:
        raw = value.upper().replace(" ", "")
        if len(raw) != 8 or not raw[:2].isalpha() or not raw[2:].isdigit():
            raise InvalidInputError(f"Passaporte deve ter 2 letras + 6 dígitos, recebeu {value}")
        return {"passaporte": raw}


class PIX(DocumentScheme):
    name = "pix-br"
    country = "BR"
    family = "financeiro"
    summary = "Chave PIX: CPF, CNPJ, email, telefone ou chave aleatória (UUID)"
    mask = None

    _cpf_scheme: CPF | None = None
    _cnpj_scheme: CNPJ | None = None

    def _ensure_schemes(self) -> None:
        if self._cpf_scheme is None:
            object.__setattr__(self, "_cpf_scheme", CPF())
        if self._cnpj_scheme is None:
            object.__setattr__(self, "_cnpj_scheme", CNPJ())

    def generate(self, ctx: GenContext) -> str:
        self._ensure_schemes()
        assert self._cpf_scheme is not None
        assert self._cnpj_scheme is not None

        rng = rng_for(ctx)

        kind = ctx.kind or rng.choice(["cpf", "cnpj", "email", "telefone", "aleatoria"])

        if kind == "cpf":
            cpf_ctx = GenContext(seed=rng.randint(0, 2**31 - 1))
            return self._cpf_scheme.generate(cpf_ctx)
        elif kind == "cnpj":
            cnpj_ctx = GenContext(seed=rng.randint(0, 2**31 - 1))
            return self._cnpj_scheme.generate(cnpj_ctx)
        elif kind == "email":
            local = "".join(chr(ord("a") + rng.randint(0, 25)) for _ in range(8))
            domain = rng.choice(["gmail.com", "hotmail.com", "yahoo.com"])
            return f"{local}@{domain}"
        elif kind == "telefone":
            ddd = rng.randint(11, 99)
            numero = "".join(str(rng.randint(0, 9)) for _ in range(8))
            return f"+55{ddd}{numero}"
        else:
            import uuid
            return str(uuid.uuid4())

    def parse(self, value: str) -> dict[str, Any]:
        self._ensure_schemes()
        assert self._cpf_scheme is not None
        assert self._cnpj_scheme is not None

        try:
            self._cpf_scheme.parse(value)
            return {"pix": value, "tipo": "cpf"}
        except InvalidInputError:
            pass

        try:
            self._cnpj_scheme.parse(value)
            return {"pix": value, "tipo": "cnpj"}
        except InvalidInputError:
            pass

        if "@" in value:
            return {"pix": value, "tipo": "email"}

        if value.startswith("+55"):
            return {"pix": value, "tipo": "telefone"}

        try:
            import uuid
            uuid.UUID(value)
            return {"pix": value, "tipo": "aleatoria"}
        except (ValueError, ImportError):
            pass

        raise InvalidInputError(f"PIX inválido: {value}")


class CNH(DocumentScheme):
    name = "cnh-br"
    country = "BR"
    family = "condução"
    summary = "CNH: Carteira Nacional de Habilitação (11 dígitos, formato apenas)"
    mask = "###########"
    available = True

    def generate(self, ctx: GenContext) -> str:
        rng = rng_for(ctx)
        return "".join(str(rng.randint(0, 9)) for _ in range(11))

    def parse(self, value: str) -> dict[str, Any]:
        raw = strip_mask(value)
        if len(raw) != 11 or not raw.isdigit():
            raise InvalidInputError(f"CNH deve ter 11 dígitos, recebeu {len(raw)}")
        return {"cnh": raw}


def build() -> list[DocumentScheme]:
    """Retorna os esquemas de documento brasileiro."""
    return [
        CPF(),
        CNPJ(),
        RG(),
        CNS(),
        PIS(),
        TituloEleitor(),
        RENAVAM(),
        Placa(),
        Passaporte(),
        PIX(),
        CNH(),
    ]
