from __future__ import annotations

from typing import Callable, Optional


class DebounceHook:
    """Delay a callback while replacing stale scheduled work."""

    def __init__(self, scheduler, delay_ms: int, callback: Callable[[], None]):
        self.scheduler = scheduler
        self.delay_ms = delay_ms
        self.callback = callback
        self.job: Optional[str] = None

    def schedule(self) -> None:
        """Schedule the callback once after the configured quiet period."""
        self.cancel()
        self.job = self.scheduler.after(self.delay_ms, self._run)

    def cancel(self) -> None:
        if self.job:
            self.scheduler.after_cancel(self.job)
            self.job = None

    def flush(self) -> None:
        """Cancel pending work and run the callback immediately."""
        self.cancel()
        self.callback()

    def _run(self) -> None:
        self.job = None
        self.callback()


Debouncer = DebounceHook
