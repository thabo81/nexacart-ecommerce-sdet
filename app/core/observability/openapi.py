"""Keeps the OpenAPI document truthful about the error contract (NFR-024, FR-106).

FastAPI documents 422 with its own HTTPValidationError, which is not what this API returns.
This replaces it with the real ErrorEnvelope and declares X-Request-ID on every response.
"""

from typing import Any

from fastapi import FastAPI

from app.core.errors import ErrorEnvelope
from app.core.observability.request_context import REQUEST_ID_HEADER

_ENVELOPE_REF = {"$ref": "#/components/schemas/ErrorEnvelope"}
_HEADER_REF = {"$ref": f"#/components/headers/{REQUEST_ID_HEADER}"}
_HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def _postprocess(schema: dict[str, Any]) -> None:
    components = schema.setdefault("components", {})
    schemas = components.setdefault("schemas", {})

    envelope = ErrorEnvelope.model_json_schema(ref_template="#/components/schemas/{model}")
    for name, definition in envelope.pop("$defs", {}).items():
        schemas.setdefault(name, definition)
    schemas["ErrorEnvelope"] = envelope
    schemas.pop("HTTPValidationError", None)
    schemas.pop("ValidationError", None)

    components.setdefault("headers", {})[REQUEST_ID_HEADER] = {
        "description": "Correlation ID, also repeated in error envelopes and structured logs.",
        "schema": {"type": "string"},
    }

    for path_item in schema.get("paths", {}).values():
        for method, operation in path_item.items():
            if method not in _HTTP_METHODS:
                continue
            for status, response in operation.get("responses", {}).items():
                if status == "422":
                    response["description"] = "Validation error"
                    response["content"] = {"application/json": {"schema": _ENVELOPE_REF}}
                response.setdefault("headers", {})[REQUEST_ID_HEADER] = _HEADER_REF


def install_openapi(app: FastAPI) -> None:
    def openapi() -> dict[str, Any]:
        if app.openapi_schema is None:
            schema = FastAPI.openapi(app)
            _postprocess(schema)
            app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = openapi  # type: ignore[method-assign]
