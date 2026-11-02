"""Dependency checks used by the readiness endpoint and the worker."""

import logging

from sqlalchemy import Engine, text

logger = logging.getLogger("nexacart.health")


def database_is_reachable(engine: Engine) -> bool:
    """Run a lightweight query on a pooled connection; any failure means "not reachable".

    Only the exception class is logged: driver messages can echo connection details.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("database check failed: %s", type(exc).__name__)
        return False
    return True
