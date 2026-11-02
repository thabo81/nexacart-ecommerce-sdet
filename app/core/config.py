"""Typed, validated configuration read from environment variables (and a local .env)."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# BR-016: the approved absolute upper bound for page_size. Configuration may lower the effective
# limit (PAGE_SIZE_MAX) but can never raise it above this contract value.
PAGE_SIZE_CONTRACT_MAX = 48


class Settings(BaseSettings):
    """Application settings. Required values have no default, so startup fails clearly."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["local", "test", "production"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    database_url: SecretStr
    build_sha: str = "unknown"  # recorded in structured logs
    page_size_default: int = Field(default=12, ge=1, le=PAGE_SIZE_CONTRACT_MAX)  # PAGE_SIZE_DEFAULT
    page_size_max: int = Field(default=48, ge=1, le=PAGE_SIZE_CONTRACT_MAX)  # PAGE_SIZE_MAX

    @model_validator(mode="after")
    def _page_size_default_within_max(self) -> "Settings":
        if self.page_size_default > self.page_size_max:
            raise ValueError(
                f"PAGE_SIZE_DEFAULT ({self.page_size_default}) must not exceed "
                f"PAGE_SIZE_MAX ({self.page_size_max})"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
