"""Configurable pagination (BR-016): effective settings drive validation and the OpenAPI doc."""

from typing import Any

import pytest
from pydantic import ValidationError

from app.core.config import PAGE_SIZE_CONTRACT_MAX, Settings
from app.core.errors import ErrorCode
from tests.api.conftest import PROBE, TOTAL_ITEMS, Probe, ProbeFactory, assert_envelope


def page_size_param(client_spec: dict[str, Any]) -> dict[str, Any]:
    params = client_spec["paths"][f"{PROBE}/items"]["get"]["parameters"]
    return next(p for p in params if p["name"] == "page_size")


def page_param(client_spec: dict[str, Any]) -> dict[str, Any]:
    params = client_spec["paths"][f"{PROBE}/items"]["get"]["parameters"]
    return next(p for p in params if p["name"] == "page")


class TestDefaultConfiguration:
    def test_defaults_are_12_and_48(self, settings: Settings) -> None:
        assert (settings.page_size_default, settings.page_size_max) == (12, 48)
        assert PAGE_SIZE_CONTRACT_MAX == 48

    def test_absent_page_size_uses_the_default(self, probe: Probe) -> None:
        body = probe.client.get(f"{PROBE}/items").json()
        assert (body["page"], body["page_size"], len(body["items"])) == (1, 12, 12)
        assert (body["total_items"], body["total_pages"]) == (TOTAL_ITEMS, 3)

    def test_maximum_is_accepted_and_one_above_is_rejected(self, probe: Probe) -> None:
        assert probe.client.get(f"{PROBE}/items?page_size=48").status_code == 200
        response = probe.client.get(f"{PROBE}/items?page_size=49")
        error = assert_envelope(response, 422, ErrorCode.VALIDATION_ERROR)
        assert [d["field"] for d in error["details"]] == ["query.page_size"]

    @pytest.mark.parametrize(
        "query", ["page=0", "page=-3", "page=abc", "page_size=0", "page_size=x"]
    )
    def test_invalid_values_are_422_validation_error(self, probe: Probe, query: str) -> None:
        assert_envelope(probe.client.get(f"{PROBE}/items?{query}"), 422, ErrorCode.VALIDATION_ERROR)

    def test_page_beyond_the_last_is_200_empty_with_correct_metadata(self, probe: Probe) -> None:
        response = probe.client.get(f"{PROBE}/items?page=99")
        assert response.status_code == 200
        body = response.json()
        assert body["items"] == []
        assert (body["page"], body["page_size"]) == (99, 12)
        assert (body["total_items"], body["total_pages"]) == (TOTAL_ITEMS, 3)

    def test_openapi_publishes_the_effective_defaults(self, probe: Probe) -> None:
        spec = probe.client.get("/api/v1/openapi.json").json()
        assert page_size_param(spec)["schema"] == {
            "type": "integer",
            "title": "Page Size",
            "minimum": 1,
            "maximum": 48,
            "default": 12,
        }
        assert page_size_param(spec)["required"] is False
        assert page_param(spec)["schema"]["minimum"] == 1
        assert page_param(spec)["schema"]["default"] == 1


class TestAlternateValidConfiguration:
    def test_lower_maximum_is_enforced_by_validation(self, probe_factory: ProbeFactory) -> None:
        probe = probe_factory(page_size_default=5, page_size_max=20)
        assert probe.client.get(f"{PROBE}/items?page_size=20").status_code == 200
        response = probe.client.get(f"{PROBE}/items?page_size=21")
        error = assert_envelope(response, 422, ErrorCode.VALIDATION_ERROR)
        assert "20" in error["details"][0]["message"]
        assert error["details"][0]["field"] == "query.page_size"
        # 30..48 are valid under the contract but exceed this deployment's effective maximum
        assert probe.client.get(f"{PROBE}/items?page_size=48").status_code == 422

    def test_lower_default_is_used_when_page_size_is_absent(
        self, probe_factory: ProbeFactory
    ) -> None:
        probe = probe_factory(page_size_default=5, page_size_max=20)
        body = probe.client.get(f"{PROBE}/items").json()
        assert (body["page_size"], len(body["items"]), body["total_pages"]) == (5, 5, 6)

    def test_openapi_agrees_with_the_effective_settings(self, probe_factory: ProbeFactory) -> None:
        probe = probe_factory(page_size_default=5, page_size_max=20)
        schema = page_size_param(probe.client.get("/api/v1/openapi.json").json())["schema"]
        assert (schema["default"], schema["maximum"], schema["minimum"]) == (5, 20, 1)

    def test_each_app_publishes_its_own_settings(self, probe_factory: ProbeFactory) -> None:
        small = probe_factory(page_size_default=2, page_size_max=4)
        default = probe_factory()
        small_schema = page_size_param(small.client.get("/api/v1/openapi.json").json())["schema"]
        default_schema = page_size_param(default.client.get("/api/v1/openapi.json").json())[
            "schema"
        ]
        assert (small_schema["maximum"], default_schema["maximum"]) == (4, 48)

    def test_default_equal_to_max_is_valid(self, probe_factory: ProbeFactory) -> None:
        probe = probe_factory(page_size_default=10, page_size_max=10)
        assert probe.client.get(f"{PROBE}/items").json()["page_size"] == 10

    def test_marker_and_nullable_artifacts_do_not_leak_into_the_document(
        self, probe_factory: ProbeFactory
    ) -> None:
        text = probe_factory().client.get("/api/v1/openapi.json").text
        assert "x-pagination" not in text


class TestInvalidConfiguration:
    @pytest.mark.parametrize(
        "overrides",
        [
            {"page_size_max": 49},  # cannot exceed the approved contract
            {"page_size_max": 100},
            {"page_size_default": 49},
            {"page_size_max": 0},
            {"page_size_default": 0},
            {"page_size_max": -1},
            {"page_size_default": 20, "page_size_max": 10},  # default above max
        ],
    )
    def test_inconsistent_settings_fail_validation(
        self, settings_factory: Any, overrides: dict[str, int]
    ) -> None:
        with pytest.raises(ValidationError):
            settings_factory(**overrides)

    def test_default_above_max_error_names_both_variables(self, settings_factory: Any) -> None:
        with pytest.raises(ValidationError, match=r"PAGE_SIZE_DEFAULT.*PAGE_SIZE_MAX"):
            settings_factory(page_size_default=20, page_size_max=10)

    def test_environment_variables_are_read_and_validated(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:placeholder@localhost/x")
        monkeypatch.setenv("PAGE_SIZE_DEFAULT", "6")
        monkeypatch.setenv("PAGE_SIZE_MAX", "24")
        settings = Settings(_env_file=None)
        assert (settings.page_size_default, settings.page_size_max) == (6, 24)
        monkeypatch.setenv("PAGE_SIZE_MAX", "49")
        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_startup_fails_clearly_with_invalid_configuration(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app.core.config import get_settings

        monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:placeholder@localhost/x")
        monkeypatch.setenv("PAGE_SIZE_MAX", "200")
        get_settings.cache_clear()
        try:
            with pytest.raises(ValidationError, match="page_size_max"):
                get_settings()
        finally:
            get_settings.cache_clear()
