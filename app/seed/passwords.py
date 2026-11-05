"""Argon2id hashing for seed accounts; plaintext is never logged."""

from argon2 import PasswordHasher

from app.seed.guard import SeedGuardError, validate_password
from app.seed.settings import SeedSettings

_hasher = PasswordHasher()  # argon2-cffi default type is Argon2id


def password_for(settings: SeedSettings, variable: str) -> str:
    secret = getattr(settings, variable)
    env_name = variable.upper()
    if secret is None:
        raise SeedGuardError(
            f"{env_name} is not set. Supply local/test seed passwords via the environment "
            "or an untracked .env."
        )
    return validate_password(secret.get_secret_value(), env_name)


def hash_password(plaintext: str) -> str:
    return _hasher.hash(plaintext)
