from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from app.services import PomodoroService
from app.ui.types import Scheduler, StateChangeCallback


@dataclass(frozen=True)
class PomodoroState:
    session_id: Optional[str]
    remaining_seconds: int
    scheduled_job: Optional[str]


class PomodoroHook:
    """Coordinates Pomodoro service state with Tk's scheduled callbacks."""

    def __init__(self, scheduler: Scheduler, service: PomodoroService, on_change: StateChangeCallback):
        self.scheduler = scheduler
        self.service = service
        self.on_change = on_change
        self.session_id: Optional[str] = None
        self.remaining = 0
        self.job: Optional[str] = None

    @property
    def state(self) -> PomodoroState:
        return PomodoroState(self.session_id, self.remaining, self.job)

    def start(self, duration_seconds: int, work_item_id: Optional[str]) -> None:
        if self.session_id:
            return
        session = self.service.start(duration_seconds=duration_seconds, work_item_id=work_item_id)
        self.session_id = session.id
        self.remaining = session.duration_seconds
        self.on_change("running", self.remaining)
        self._schedule_tick()

    def pause(self) -> None:
        if not self.session_id:
            return
        self._cancel_tick()
        self.service.pause(self.session_id)
        self.on_change("paused", self.remaining)

    def resume(self) -> None:
        if not self.session_id:
            return
        self.service.resume(self.session_id)
        self.on_change("running", self.remaining)
        self._schedule_tick()

    def reset(self) -> None:
        self._cancel_tick()
        if self.session_id:
            self.service.reset(self.session_id)
        self.session_id = None
        self.remaining = 0
        self.on_change("ready", 0)

    def _schedule_tick(self) -> None:
        self._cancel_tick()
        self.job = self.scheduler.after(1000, self._tick)

    def _tick(self) -> None:
        self.job = None
        if not self.session_id:
            return
        self.remaining -= 1
        if self.remaining <= 0:
            self.service.complete(self.session_id)
            self.session_id = None
            self.on_change("complete", 0)
            return
        self.on_change("running", self.remaining)
        self._schedule_tick()

    def _cancel_tick(self) -> None:
        if self.job:
            self.scheduler.after_cancel(self.job)
            self.job = None


PomodoroController = PomodoroHook
