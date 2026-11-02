"""The code/status catalogue must match PRD Appendix A exactly (TR-011)."""

import re
from pathlib import Path

from app.core.errors import ERROR_STATUS, AppError, ErrorCode

PRD = Path(__file__).resolve().parents[2] / "docs" / "planning" / "PRD.md"
FRAMEWORK_CODES = {"BAD_REQUEST": 400, "METHOD_NOT_ALLOWED": 405, "INTERNAL_ERROR": 500}


def _prd_catalogue() -> dict[int, set[str]]:
    text = PRD.read_text(encoding="utf-8")
    section = text.split("## Appendix A", 1)[1].split("## Appendix B", 1)[0]
    catalogue: dict[int, set[str]] = {}
    for row in re.finditer(r"^\| (\d{3}) \| (.+) \|$", section, re.MULTILINE):
        catalogue[int(row.group(1))] = set(re.findall(r"`([A-Z_]+)`", row.group(2)))
    return catalogue


def test_codes_and_statuses_match_the_prd_appendix_exactly() -> None:
    prd = _prd_catalogue()
    assert prd, "failed to parse PRD Appendix A"
    ours: dict[int, set[str]] = {}
    for code, status in ERROR_STATUS.items():
        ours.setdefault(status, set()).add(code.value)
    assert ours == prd


def test_owner_approved_framework_codes_are_in_the_prd_with_the_approved_statuses() -> None:
    prd = _prd_catalogue()
    for code, status in FRAMEWORK_CODES.items():
        assert code in prd[status], f"{code} missing from PRD Appendix A under {status}"
        assert ERROR_STATUS[ErrorCode(code)] == status


def test_no_proposed_code_concept_remains() -> None:
    import app.core.errors as errors

    assert not hasattr(errors, "PROPOSED_CODES")


def test_every_code_has_exactly_one_status() -> None:
    assert set(ERROR_STATUS) == set(ErrorCode)


def test_not_ready_is_503_and_validation_error_is_422_and_not_found_is_404() -> None:
    assert ERROR_STATUS[ErrorCode.NOT_READY] == 503
    assert ERROR_STATUS[ErrorCode.VALIDATION_ERROR] == 422
    assert ERROR_STATUS[ErrorCode.NOT_FOUND] == 404


def test_app_error_status_comes_from_the_catalogue() -> None:
    error = AppError(ErrorCode.CART_LOCKED, "locked", details=[{"field": "cart"}])
    assert error.status_code == 409
    assert error.details == [{"field": "cart"}]
    assert AppError(ErrorCode.NOT_READY, "x").status_code == 503
