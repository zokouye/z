from __future__ import annotations

import threading
import time
from collections.abc import Callable

from .logging_config import get_logger

logger = get_logger(__name__)


class JobScheduler:
    """A simple interval-based scheduler running in a background thread."""

    def __init__(self) -> None:
        self._jobs: list[tuple[float, Callable[[], None]]] = []
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def add_job(self, interval_seconds: float, func: Callable[[], None]) -> None:
        self._jobs.append((interval_seconds, func))

    def _run(self) -> None:
        next_run = [time.time() + interval for interval, _ in self._jobs]
        while not self._stop.is_set():
            now = time.time()
            for idx, (interval, func) in enumerate(self._jobs):
                if now >= next_run[idx]:
                    try:
                        func()
                    except Exception as exc:  # pragma: no cover
                        logger.exception("Scheduled job failed: %s", exc)
                    next_run[idx] = now + interval
            time.sleep(1)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
