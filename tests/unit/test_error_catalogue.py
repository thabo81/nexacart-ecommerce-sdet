"""The code/status catalogue must match PRD Appendix A (TR-011); extras must stay flagged."""

import re
from pathlib import Path

from app.core.errors import ERROR_STATUS, PROPOSED_CODES, AppError, ErrorCode

PRD = Path(__file__).resolve().parents[2] / "docs" / "planning" / "PRD.md"


def _prd_catalogue() -> dict[int, set[str]]:
    text = PRD.read_text(encoding="utf-8")
    section = text.split("## Appendix A", 1)[1].split("## Appendix B", 1)[0]
    catalogue: dict[int, set[str]] = {}
    for row in re.finditer(r"^\| (\d{3}) \| (.+) \|$", section, re.MULTILINE):
        catalogue[int(row.group(1))] = set(re.findall(r"`([A-Z_]+)`", row.group(2)))
    return catalogue


def test_approved_codes_and_statuses_match_the_prd_appendix() -> None:
    prd = _prd_catalogue()
    assert prd, "failed to parse PRD Appendix A"
    ours: dict[int, set[str]] = {}
    for code, status in ERROR_STATUS.items():
        if code not in PROPOSED_CODES:
            ours.setdefault(status, set()).add(code.value)
    assert ours == prd


def test_proposed_codes_are_not_in_the_prd_and_are_exactly_three() -> None:
    prd_codes = {c for codes in _prd_catalogue().values() for c in codes}
    assert {c.value for c in PROPOSED_CODES}.isdisjoint(prd_codes)
    assert {c.value for c in PROPOSED_CODES} == {
        "BAD_REQUEST",
        "METHOD_NOT_ALLOWED",
        "INTERNAL_ERROR",
    }


def test_every_code_has_exactly_one_status() -> None:
    assert set(ERROR_STATUS) == set(ErrorCode)


def test_app_error_status_comes_from_the_catalogue() -> None:
    error = AppError(ErrorCode.CART_LOCKED, "locked", details=[{"field": "cart"}])
    assert error.status_code == 409
    assert error.details == [{"field": "cart"}]
    assert AppError(ErrorCode.NOT_READY, "x").status_code == 503
