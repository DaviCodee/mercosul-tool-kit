"""API HTTP do toolkit, gerada a partir do registro de operações.

Rotas:
    GET  /operations                  lista as operações
    GET  /operations/{name}/schema    schema JSON dos parâmetros
    POST /operations/{name}           executa a operação (corpo: params JSON)

Como documentos são texto, o valor de entrada (quando há) viaja dentro de ``params``;
a resposta é sempre o ``meta`` da operação em JSON.
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from mercosultoolkit.core.errors import (
    InvalidInputError,
    MercosulToolkitError,
    MissingDependencyError,
)
from mercosultoolkit.core.operation import DocumentOperation
from mercosultoolkit.core.registry import all_operations, get_operation


def create_app() -> FastAPI:
    app = FastAPI(title="mercosultoolkit", version="0.1.0")

    @app.get("/operations")
    def list_operations() -> list[dict[str, str]]:
        return [
            {"name": op.name, "category": op.category, "summary": op.summary}
            for op in all_operations()
        ]

    @app.get("/operations/{name}/schema")
    def operation_schema(name: str) -> dict[str, Any]:
        return _lookup(name).params_model.model_json_schema()

    @app.post("/operations/{name}")
    async def run_operation(name: str, params: str = Form(default="{}")) -> Any:
        op = _lookup(name)
        try:
            payload = json.loads(params or "{}")
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=422, detail=f"params não é JSON válido: {exc}") from exc
        try:
            model = op.params_model(**payload)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=json.loads(exc.json())) from exc

        try:
            result = op.execute([], model)
        except MissingDependencyError as exc:
            raise HTTPException(status_code=501, detail=str(exc)) from exc
        except InvalidInputError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except MercosulToolkitError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return JSONResponse(result.meta)

    return app


def _lookup(name: str) -> DocumentOperation[Any]:
    try:
        return get_operation(name)
    except MercosulToolkitError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


app = create_app()
