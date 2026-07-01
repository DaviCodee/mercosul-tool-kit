"""CLI do toolkit, gerada a partir do registro de operações.

Cada operação registrada vira um subcomando próprio, com flags derivadas do seu modelo
de parâmetros Pydantic:

    mtk list                              lista as operações disponíveis
    mtk schema <operacao>                 mostra o schema JSON dos parâmetros
    mtk list-documents                    lista o catálogo de documentos
    mtk generate --document cpf --count 3 gera documentos
    mtk inspect --value <doc>             extrai metadados de um documento
    mtk validate --value <doc>            valida (ou detecta) um documento
    mtk mask --value <doc>                aplica/remove máscara de exibição

Documentos são texto: a saída de ``generate`` é impressa um por linha (ou gravada com
``-o``); as demais operações imprimem os metadados como JSON.
"""

from __future__ import annotations

import json
import types
from pathlib import Path
from typing import Any, Literal, Union, get_args, get_origin

import click

from mercosultoolkit.core.errors import MercosulToolkitError
from mercosultoolkit.core.operation import DocumentOperation
from mercosultoolkit.core.registry import all_operations, get_operation

_RESERVED = {"list", "schema"}
_PY_TYPES: dict[type, type] = {int: int, float: float, str: str}


@click.group(help="Concentrador de operações sobre documentos do Mercosul.")
def app() -> None:
    pass


@app.command("list")
def list_command() -> None:
    """Lista todas as operações registradas."""
    for operation in all_operations():
        click.echo(f"{operation.name:<16} [{operation.category}] {operation.summary}")


@app.command("schema")
@click.argument("operation")
def schema_command(operation: str) -> None:
    """Mostra o schema JSON dos parâmetros de uma operação."""
    op = _lookup(operation)
    click.echo(json.dumps(op.params_model.model_json_schema(), indent=2, ensure_ascii=False))


def _unwrap_optional(annotation: Any) -> tuple[Any, bool]:
    origin = get_origin(annotation)
    if origin is Union or origin is types.UnionType:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        return args[0], True
    return annotation, False


def _build_option(name: str, field: Any) -> click.Option:
    flag = "--" + name.replace("_", "-")
    annotation, _optional = _unwrap_optional(field.annotation)
    origin = get_origin(annotation)
    required = field.is_required()
    default = None if field.is_required() else field.default

    if annotation is bool:
        return click.Option(
            [f"{flag}/--no-{name.replace('_', '-')}", name],
            default=default, help=field.description or "",
        )
    if origin is Literal:
        choices = [str(value) for value in get_args(annotation)]
        return click.Option(
            [flag, name], type=click.Choice(choices), default=default,
            required=required, help=field.description or "",
        )
    return click.Option(
        [flag, name], type=_PY_TYPES.get(annotation, str), default=default,
        required=required, help=field.description or "",
    )


def _collect_params(
    op: DocumentOperation[Any], ctx: click.Context, raw: dict[str, Any]
) -> dict[str, Any]:
    fields = op.params_model.model_fields
    payload: dict[str, Any] = {}
    json_blob = raw.get("json_params")
    if json_blob:
        payload.update(json.loads(json_blob))
    for name in fields:
        if ctx.get_parameter_source(name) == click.core.ParameterSource.DEFAULT:
            continue
        payload[name] = raw[name]
    return payload


def _make_operation_command(op: DocumentOperation[Any]) -> click.Command:
    def callback(**raw: Any) -> None:
        ctx = click.get_current_context()
        out = raw.pop("out")
        try:
            payload = _collect_params(op, ctx, raw)
            params = op.params_model(**payload)
            result = op.execute([], params)
        except (MercosulToolkitError, OSError, ValueError) as exc:
            raise click.ClickException(str(exc)) from exc
        _emit(result.meta, out)

    params: list[click.Parameter] = [
        click.Option(
            ["-o", "--out", "out"], type=click.Path(path_type=Path),
            help="arquivo de saída (para 'generate'); sem ele imprime na tela",
        ),
        click.Option(["--json", "json_params"], help="parâmetros como objeto JSON"),
    ]
    params.extend(
        _build_option(name, field) for name, field in op.params_model.model_fields.items()
    )
    return click.Command(name=op.name, params=params, callback=callback, help=op.summary)


def _emit(meta: dict[str, Any], out: Path | None) -> None:
    if "values" in meta:
        text = "\n".join(meta["values"])
        if out is not None:
            out.write_text(text + "\n", encoding="utf-8")
            click.echo(f"escrito: {out} ({meta['count']} documento(s))")
        else:
            click.echo(text)
        return
    if "documents" in meta:
        _print_documents(meta["documents"])
        return
    click.echo(json.dumps(meta, indent=2, ensure_ascii=False))


def _print_documents(documents: list[dict[str, Any]]) -> None:
    for doc in documents:
        mask_str = "" if doc["mask"] is None else f"máscara: {doc['mask']}"
        status = "" if doc["available"] else f"  indisponível ({doc['reason']})"
        click.echo(
            f"{doc['name']:<16} [{doc['country']}] {doc['family']:<16} "
            f"{mask_str:<30} {doc['summary']}{status}"
        )


def _lookup(name: str) -> DocumentOperation[Any]:
    try:
        return get_operation(name)
    except MercosulToolkitError as exc:
        raise click.ClickException(str(exc)) from exc


def _register_operation_commands() -> None:
    for operation in all_operations():
        if operation.name in _RESERVED:
            continue
        app.add_command(_make_operation_command(operation))


_register_operation_commands()


if __name__ == "__main__":  # pragma: no cover
    app()
