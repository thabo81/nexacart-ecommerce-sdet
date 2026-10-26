"""Pagination conventions (BR-016, FR-021, NFR-023).

`page` >= 1 (default 1); `page_size` 1-48 (default 12). Out-of-range values are rejected with
422 VALIDATION_ERROR by the shared handler. A page beyond the last returns an empty `items`
list with correct metadata. Defaults mirror the PRD config values PAGE_SIZE_DEFAULT/MAX.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel

PAGE_SIZE_DEFAULT = 12
PAGE_SIZE_MAX = 48


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
    page: Annotated[int, Query(ge=1, description="1-based page number")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=PAGE_SIZE_MAX, description="Items per page (maximum 48)")
    ] = PAGE_SIZE_DEFAULT,
) -> Pagination:
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
