from __future__ import annotations

from typing import Callable, Protocol

ItemId = str
StateChangeCallback = Callable[[str, int], None]


class Scheduler(Protocol):
    def after(self, delay_ms: int, callback: Callable[[], None]) -> str: ...

    def after_cancel(self, job: str) -> None: ...
