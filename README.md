# mercosul-tool-kit

Concentrador de documentos do Mercosul: um **núcleo leve** em Python que expõe um registro de
operações, consumido por adaptadores finos de **CLI** (`mtk`) e **API** (FastAPI). A mesma
operação, definida uma vez, fica disponível na linha de comando e via HTTP.

Valida, gera e formata números de documentos oficiais dos 5 países do Mercosul (Brasil,
Argentina, Uruguai, Paraguai, Chile): CPF, CNPJ, DNI, CUIT, Cédula, RUT, RUC, Chave Pix,
placas veiculares Mercosul, e mais.

O núcleo (`mercosultoolkit.core`) depende **apenas da stdlib + Pydantic**. Os documentos
(`mercosultoolkit.documents`) usam **só a biblioteca padrão**.

## Arquitetura

```
src/mercosultoolkit/
  core/        contrato (operation), registro, params (Pydantic), io, erros
  documents/   catálogo de documentos: cpf, cnpj, rg-br, cns, pis, dni-ar, cuil-ar,
               cuit-ar, cedula-uy, rut-uy, rut-cl, cedula-py, ruc-py, placas, etc.
  operations/  generate, validate, inspect, mask, list-documents — genéricas
  cli/         main.py  — Click, um subcomando por operação (mtk)
  api/         app.py   — FastAPI gerada a partir do registro
```

Há **dois registros**: o de operações (`core/registry.py`) e o de **documentos**
(`documents/catalog.py`). As operações são genéricas e recebem o documento por parâmetro,
resolvido pelo catálogo (com aliases).

## Instalação

```bash
pip install -e ".[cli,api]"      # núcleo + CLI + API
pip install -e ".[cli,api,dev]"  # tudo, incluindo testes/lint/type-check
```

| Extra | Habilita                          |
|-------|-----------------------------------|
| `cli` | comando `mtk`                     |
| `api` | servidor FastAPI/uvicorn          |
| `dev` | pytest, ruff, mypy, httpx         |

O núcleo (`pydantic`) é sempre instalado.

## Operações

| Operação        | Categoria | Resumo                                          |
|-----------------|-----------|------------------------------------------------|
| `generate`      | geração   | Gera um ou mais documentos (válidos em DV).    |
| `validate`      | análise   | Valida (ou detecta) o tipo de um documento.    |
| `inspect`       | análise   | Extrai metadados (componentes, DVs…).          |
| `mask`          | formato   | Aplica/remove máscara de exibição.             |
| `list-documents`| catálogo  | Lista os documentos disponíveis.               |

## Uso (CLI)

```bash
mtk list                                        # operações
mtk list-documents                              # catálogo de documentos
mtk list-documents --country BR                 # apenas Brasil
mtk schema generate                             # JSON Schema dos parâmetros

mtk generate --document cpf                     # um CPF aleatório
mtk generate --document cpf --count 5           # cinco CPFs
mtk generate --document cnpj --kind alfanumerico # CNPJ alfanumérico (2026+)
mtk generate --document rut-cl                  # RUT chileno
mtk generate --document cpf --masked=false      # sem máscara

mtk validate --value 12345678909 --document cpf # valida CPF específico
mtk validate --value 12345678909                # detecta o tipo
mtk inspect  --value 12345678909                # extrai componentes
mtk mask     --value 12345678909 --document cpf # aplica máscara
mtk mask     --value 123.456.789-09 --document cpf --to unmasked
```

## Uso (API)

```bash
uvicorn mercosultoolkit.api.app:app --reload
```

```
GET  /operations                   lista as operações
GET  /operations/{name}/schema     JSON Schema dos parâmetros
POST /operations/{name}            executa (corpo: form-field `params` em JSON)
```

```bash
curl -s localhost:8000/operations/generate \
  -F 'params={"document":"cpf","count":2}'
# -> {"document":"cpf","country":"BR","count":2,"values":["...","..."]}

curl -s localhost:8000/operations/validate \
  -F 'params={"value":"12345678909"}'
# -> {"value":"12345678909","valid":true,"detected":"cpf",...}
```

## Catálogo de documentos

**Brasil:** CPF, CNPJ (numérico e alfanumérico), RG*, CNS, PIS, Título de Eleitor, RENAVAM,
Placa (antiga e Mercosul), Chave Pix.

**Argentina:** DNI, CUIL, CUIT, Patente (antiga e Mercosul).

**Uruguai:** Cédula, RUT (pessoa física e jurídica), Matrícula.

**Paraguai:** Cédula*, RUC, Placa.

**Chile:** RUT/RUN, Patente (antiga e nova).

*com ressalva: algoritmo de dígito verificador não publicamente especificado.

### Notas de fidelidade

- **CPF, CNPJ (numérico), PIS, RENAVAM, CUIL/CUIT, Cédula-UY, RUT-CL:** algoritmos bem
  documentados e independentemente verificados.
- **CNPJ alfanumérico:** novo formato 2026 da Receita Federal/Serpro; validar contra
  documentação oficial antes de usar em produção.
- **CNS, Título de Eleitor (SP/MG), RUC-PY, RUT-UY (jurídica):** algoritmos encontrados
  em fontes públicas, mas verificação contra exemplo oficial recomendada.
- **RG-BR, Cédula-PY:** sem especificação pública de dígito verificador; aceita formato/
  faixa apenas. Documentação diz o quê, não promete exatidão de validação.

## Fora do escopo (Fase 2)

As seguintes funcionalidades são documentadas aqui mas não implementadas na Fase 1:

- **Consultas / Lookups:** CEP (Brasil), DDD, IBGE (UFs e municípios), NCM, CFOP, CST,
  códigos postais dos outros países. Exigem tabelas de dados externas; escopo separado.
- **Calculadoras bancárias:** Boleto (linha digitável), DV de agência/conta. Algoritmos
  específicos por banco; fora do escopo deste projeto.

## Desenvolvimento

```bash
uv venv && uv pip install -e ".[cli,api,dev]"
uv run ruff check src tests
uv run mypy
uv run pytest
```
