"""Pagination conventions (BR-016, FR-021, NFR-023).

`page` >= 1 (default 1). `page_size` >= 1, default PAGE_SIZE_DEFAULT (12) and at most
PAGE_SIZE_MAX (48), both read from the application's settings. Settings validation guarantees
1 <= default <= max <= 48, so configuration can lower the limit but never exceed the approved
contract. Out-of-range values are rejected with 422 VALIDATION_ERROR (field paths
`query.page` / `query.page_size`). A page beyond the last returns an empty `items` list with
correct metadata. The published OpenAPI document shows the effective default and maximum.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query, Request
from pydantic import BaseModel

from app.core.config import Settings
from app.core.errors import AppError, ErrorCode

# Marks pagination parameters so OpenAPI post-processing can publish the effective settings.
PAGINATION_MARKER = "x-pagination"


@dataclass(frozen=True)
class Pagination:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def pagination_params(
    request: Request,
    page: Annotated[
        int,
        Query(
            ge=1, description="1-based page number", json_schema_extra={PAGINATION_MARKER: "page"}
        ),
    ] = 1,
    page_size: Annotated[
        int | None,
        Query(
            ge=1,
            description="Items per page (default and maximum come from configuration)",
            json_schema_extra={PAGINATION_MARKER: "page_size"},
        ),
    ] = None,
) -> Pagination:
    settings: Settings = request.app.state.settings
    if page_size is None:
        page_size = settings.page_size_default
    elif page_size > settings.page_size_max:
        raise AppError(
            ErrorCode.VALIDATION_ERROR,
            "The request is invalid.",
            details=[
                {
                    "field": "query.page_size",
                    "message": f"Input should be less than or equal to {settings.page_size_max}",
                    "type": "less_than_equal",
                }
            ],
        )
    return Pagination(page=page, page_size=page_size)


PaginationDep = Annotated[Pagination, Depends(pagination_params)]


class Page[T](BaseModel):
    """Standard paginated response: items plus page, page_size, total_items, total_pages."""

    items: list[T]
    page: int
    page_size: int
    total_items: int
    total_pages: int


def total_pages(total_items: int, page_size: int) -> int:
    return -(-total_items // page_size)


def build_page[T](items: Sequence[T], pagination: Pagination, total_items: int) -> Page[T]:
    return Page[T](
        items=list(items),
        page=pagination.page,
        page_size=pagination.page_size,
        total_items=total_items,
        total_pages=total_pages(total_items, pagination.page_size),
    )
