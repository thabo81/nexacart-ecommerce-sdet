"""Environment guard: seed and reset run only in an explicit local/test environment."""

from sqlalchemy.engine import make_url

from app.seed.settings import SeedSettings

ALLOWED_ENVS = frozenset({"local", "test"})
# Extra defence in depth: only loopback hosts and the Docker Compose service names.
ALLOWED_DB_HOSTS = frozenset(
    {"localhost", "127.0.0.1", "::1", "db", "db-test", "host.docker.internal"}
)
# Enforce environment/database pairing as a separate safety boundary.
ALLOWED_DATABASES = {"local": "nexacart", "test": "nexacart_test"}
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128
PLACEHOLDER_PREFIX = "change-me"


class SeedGuardError(RuntimeError):
    """Raised (before any database access) when a seed/reset precondition is not met."""


def assert_safe_environment(settings: SeedSettings) -> str:
    """Return the database name after verifying env, host and exact database pairing."""
    if settings.app_env not in ALLOWED_ENVS:
        raise SeedGuardError(
            "Refusing to run: APP_ENV must be explicitly set to 'local' or 'test' "
            f"(found {settings.app_env!r})."
        )
    if settings.database_url is None:
        raise SeedGuardError("Refusing to run: DATABASE_URL is not set.")

    url = make_url(settings.database_url.get_secret_value())
    if (url.host or "") not in ALLOWED_DB_HOSTS:
        raise SeedGuardError(
            "Refusing to run: the database host is not a local/Compose host. "
            "Seed and reset never target remote or public databases."
        )

    expected_database = ALLOWED_DATABASES[settings.app_env]
    if url.database != expected_database:
        raise SeedGuardError(
            "Refusing to run: "
            f"APP_ENV={settings.app_env!r} may only target database "
            f"{expected_database!r} (found {url.database!r})."
        )

    return expected_database


def validate_password(value: str, variable: str) -> str:
    if value.startswith(PLACEHOLDER_PREFIX):
        raise SeedGuardError(f"{variable} still holds the .env.example placeholder; set your own.")
    if not MIN_PASSWORD_LENGTH <= len(value) <= MAX_PASSWORD_LENGTH:
        raise SeedGuardError(
            f"{variable} must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters."
        )
    return value
