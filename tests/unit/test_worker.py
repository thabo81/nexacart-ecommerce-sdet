"""Worker lifecycle: start only with a reachable database, heartbeat, clean stop, healthcheck."""

import os
import threading
import time
from pathlib import Path

import pytest

from app.core.config import Settings
from app.worker import __main__ as worker


@pytest.fixture(autouse=True)
def _worker_env(monkeypatch: pytest.MonkeyPatch, settings: Settings) -> None:
    monkeypatch.setenv("DATABASE_URL", settings.database_url.get_secret_value())
    monkeypatch.setenv("APP_ENV", "test")


def test_worker_exits_1_when_database_unreachable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(worker, "database_is_reachable", lambda _engine: False)
    code = worker.main([], stop=threading.Event(), heartbeat_file=tmp_path / "hb")
    assert code == 1
    assert "database is not reachable" in caplog.text
    assert not (tmp_path / "hb").exists()


def test_worker_stops_cleanly_and_writes_then_removes_heartbeat(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(worker, "database_is_reachable", lambda _engine: True)
    heartbeat = tmp_path / "hb"
    stop = threading.Event()
    seen: list[bool] = []

    # Handlers can only be installed from the main thread, so main() runs inline and a timer
    # (after the first heartbeat) plays the part of SIGTERM by setting the stop event.
    def simulate_sigterm() -> None:
        seen.append(heartbeat.exists())
        stop.set()

    timer = threading.Timer(0.3, simulate_sigterm)
    timer.start()
    with caplog.at_level("INFO", logger="nexacart.worker"):
        code = worker.main([], stop=stop, heartbeat_file=heartbeat)
    timer.join()
    assert code == 0
    assert seen == [True]
    assert not heartbeat.exists()
    assert "worker started" in caplog.text
    assert "worker stopped" in caplog.text


def test_worker_restores_signal_handlers(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import signal

    monkeypatch.setattr(worker, "database_is_reachable", lambda _engine: True)
    before = signal.getsignal(signal.SIGTERM)
    stop = threading.Event()
    stop.set()
    assert worker.main([], stop=stop, heartbeat_file=tmp_path / "hb") == 0
    assert signal.getsignal(signal.SIGTERM) is before


def test_healthcheck_reflects_heartbeat_freshness(tmp_path: Path) -> None:
    heartbeat = tmp_path / "hb"
    assert worker.main(["--healthcheck"], heartbeat_file=heartbeat) == 1  # missing
    heartbeat.touch()
    assert worker.main(["--healthcheck"], heartbeat_file=heartbeat) == 0  # fresh
    stale = time.time() - worker.HEARTBEAT_MAX_AGE_SECONDS - 5
    os.utime(heartbeat, (stale, stale))
    assert worker.main(["--healthcheck"], heartbeat_file=heartbeat) == 1  # stale
