"""Pagination arithmetic (BR-016)."""

import pytest

from app.api.pagination import Pagination, build_page, total_pages


@pytest.mark.parametrize(
    ("total", "size", "expected"),
    [(0, 12, 0), (1, 12, 1), (12, 12, 1), (13, 12, 2), (30, 12, 3), (48, 48, 1), (49, 48, 2)],
)
def test_total_pages(total: int, size: int, expected: int) -> None:
    assert total_pages(total, size) == expected


def test_offset_and_limit() -> None:
    pagination = Pagination(page=3, page_size=12)
    assert (pagination.offset, pagination.limit) == (24, 12)


def test_build_page_beyond_last_keeps_metadata() -> None:
    page = build_page(list[int](), Pagination(page=9, page_size=12), total_items=30)
    assert page.model_dump() == {
        "items": [],
        "page": 9,
        "page_size": 12,
        "total_items": 30,
        "total_pages": 3,
    }
