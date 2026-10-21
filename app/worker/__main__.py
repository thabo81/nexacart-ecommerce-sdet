"""Worker entry point. Run: python -m app.worker

Reservation-expiry and refund processors are added by later backlog tasks; for now the
process validates configuration and exits.
"""

import logging

from app.core.config import get_settings

logger = logging.getLogger("nexacart.worker")


def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    logger.info("worker started (env=%s); no processors registered yet", settings.app_env)


if __name__ == "__main__":
    main()
