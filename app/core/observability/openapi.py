"""Keeps the OpenAPI document truthful about the error and pagination contracts (NFR-024).

- FastAPI documents 422 with its own HTTPValidationError, which is not what this API returns;
  it is replaced with the real ErrorEnvelope.
- Every response declares the X-Request-ID header.
- Every operation gets a `default` response referencing the shared StandardError response, so any
  status an operation does not document explicitly (404, 500, ...) has an accurate contract.
  Explicit operation-level responses (200, 409, 503, ...) are never overwritten.
- Pagination parameters publish the effective default and maximum from the app's settings.
"""

from typing import Any

from fastapi import FastAPI

from app.api.pagination import PAGINATION_MARKER
from app.core.config import Settings
from app.core.errors import ErrorEnvelope
from app.core.observability.request_context import REQUEST_ID_HEADER

_ENVELOPE_REF = {"$ref": "#/components/schemas/ErrorEnvelope"}
_HEADER_REF = {"$ref": f"#/components/headers/{REQUEST_ID_HEADER}"}
_STANDARD_ERROR_REF = {"$ref": "#/components/responses/StandardError"}
_HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
_VALIDATION_EXAMPLE = {
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "The request is invalid.",
        "details": [
            {
                "field": "query.page_size",
                "message": "Input should be less than or equal to 48",
                "type": "less_than_equal",
            }
        ],
        "request_id": "3f1c2d4e-5a6b-4c7d-8e9f-0a1b2c3d4e5f",
    }
}


def _publish_pagination_settings(operation: dict[str, Any], settings: Settings) -> None:
    for parameter in operation.get("parameters", []):
        schema = parameter.get("schema", {})
        marker = schema.pop(PAGINATION_MARKER, None)
        if marker == "page_size":
            parameter["schema"] = {
                "type": "integer",
                "title": "Page Size",
                "minimum": 1,
                "maximum": settings.page_size_max,
                "default": settings.page_size_default,
            }
            parameter["required"] = False


def _postprocess(schema: dict[str, Any], settings: Settings) -> None:
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
    components.setdefault("responses", {})["StandardError"] = {
        "description": (
            "Standard error envelope. Used for any status an operation does not document "
            "explicitly, and by framework-level errors that belong to no operation "
            "(unknown route 404, unsupported method 405, unexpected error 500)."
        ),
        "headers": {REQUEST_ID_HEADER: _HEADER_REF},
        "content": {"application/json": {"schema": _ENVELOPE_REF}},
    }

    for path_item in schema.get("paths", {}).values():
        for method, operation in path_item.items():
            if method not in _HTTP_METHODS:
                continue
            _publish_pagination_settings(operation, settings)
            responses = operation.setdefault("responses", {})
            for status, response in responses.items():
                if "$ref" in response:
                    continue
                if status == "422":
                    response["description"] = (
                        "VALIDATION_ERROR. details[] lists {field, message, type}; field paths "
                        "include the input location (query., body., path., header.)."
                    )
                    response["content"] = {
                        "application/json": {
                            "schema": _ENVELOPE_REF,
                            "example": _VALIDATION_EXAMPLE,
                        }
                    }
                response.setdefault("headers", {})[REQUEST_ID_HEADER] = _HEADER_REF
            responses.setdefault("default", _STANDARD_ERROR_REF)


def install_openapi(app: FastAPI) -> None:
    def openapi() -> dict[str, Any]:
        if app.openapi_schema is None:
            schema = FastAPI.openapi(app)
            _postprocess(schema, app.state.settings)
            app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = openapi  # type: ignore[method-assign]
