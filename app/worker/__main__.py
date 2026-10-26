"""Worker entry point. Run: python -m app.worker  (health probe: python -m app.worker --healthcheck)

Scaffold only: it verifies database connectivity, then idles with a heartbeat until it receives
SIGTERM/SIGINT. Reservation-expiry and refund processors are added by later backlog tasks.
"""

import argparse
import logging
import signal
import tempfile
import threading
import time
from collections.abc import Sequence
from pathlib import Path
from types import FrameType

from app.core.config import get_settings
from app.core.observability.health import database_is_reachable
from app.core.observability.structured_logging import configure_logging
from app.persistence.session import create_db_engine

logger = logging.getLogger("nexacart.worker")

HEARTBEAT_FILE = Path(tempfile.gettempdir()) / "nexacart-worker-heartbeat"
HEARTBEAT_INTERVAL_SECONDS = 5.0
HEARTBEAT_MAX_AGE_SECONDS = 30.0


def heartbeat_is_fresh(
    path: Path = HEARTBEAT_FILE, max_age: float = HEARTBEAT_MAX_AGE_SECONDS
) -> bool:
    try:
        return (time.time() - path.stat().st_mtime) <= max_age
    except FileNotFoundError:
        return False


def main(
    argv: Sequence[str] | None = None,
    *,
    stop: threading.Event | None = None,
    heartbeat_file: Path = HEARTBEAT_FILE,
) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.worker")
    parser.add_argument("--healthcheck", action="store_true", help="exit 0 if the worker is alive")
    args = parser.parse_args(argv)
    if args.healthcheck:
        return 0 if heartbeat_is_fresh(heartbeat_file) else 1

    settings = get_settings()
    configure_logging(settings)
    stop = stop or threading.Event()

    def request_stop(signum: int, _frame: FrameType | None) -> None:
        logger.info("received signal %s, shutting down", signal.Signals(signum).name)
        stop.set()

    previous = {sig: signal.signal(sig, request_stop) for sig in (signal.SIGTERM, signal.SIGINT)}
    engine = create_db_engine(settings)
    try:
        if not database_is_reachable(engine):
            logger.error("database is not reachable; worker cannot start")
            return 1
        logger.info("worker started (env=%s); no processors registered yet", settings.app_env)
        while not stop.is_set():
            heartbeat_file.touch()
            stop.wait(HEARTBEAT_INTERVAL_SECONDS)
        logger.info("worker stopped")
        return 0
    finally:
        engine.dispose()
        heartbeat_file.unlink(missing_ok=True)
        for sig, handler in previous.items():
            signal.signal(sig, handler)


if __name__ == "__main__":
    raise SystemExit(main())
