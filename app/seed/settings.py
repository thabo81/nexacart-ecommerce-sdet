"""Seed-only settings. Passwords exist only in local/test configuration (TR-003, NFR-022)."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SeedSettings(BaseSettings):
    """Read from the process environment and an optional untracked .env file.

    ``app_env`` deliberately has no default: seed/reset fail closed unless APP_ENV is explicit.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str | None = None
    database_url: SecretStr | None = None
    seed_password_admin: SecretStr | None = None
    seed_password_customer: SecretStr | None = None
    seed_password_history: SecretStr | None = None
    seed_password_reviewer: SecretStr | None = None
