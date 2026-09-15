from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.models import WorkItem
from app.services import CommentService, NoteService, PomodoroService, TodoService, WorkItemService
from app.ui.types import RefreshCallback


@dataclass(frozen=True)
class DashboardHookResult:
    """Typed public surface exposed to the Dashboard view."""

    todo_service: TodoService
    note_service: NoteService
    pomodoro_service: PomodoroService
    work_item_service: WorkItemService
    comment_service: CommentService
    register_refreshers: Callable[["DashboardRefreshers"], None]
    refresh_all: RefreshCallback
    get_work_item: Callable[[str], WorkItem]


@dataclass(frozen=True)
class DashboardRefreshers:
    todos: RefreshCallback
    notes: RefreshCallback
    work_board: RefreshCallback


class DashboardHook:
    """Owns Dashboard-level service coordination and refresh state."""

    def __init__(self, todo_service: TodoService, note_service: NoteService, pomodoro_service: PomodoroService, work_item_service: WorkItemService, comment_service: CommentService):
        self.result = DashboardHookResult(
            todo_service=todo_service,
            note_service=note_service,
            pomodoro_service=pomodoro_service,
            work_item_service=work_item_service,
            comment_service=comment_service,
            register_refreshers=self.register_refreshers,
            refresh_all=self.refresh_all,
            get_work_item=work_item_service.get,
        )
        self._refresh_callbacks: list[RefreshCallback] = []

    def register_refreshers(self, refreshers: DashboardRefreshers) -> None:
        self._refresh_callbacks = [refreshers.todos, refreshers.notes, refreshers.work_board]

    def refresh_all(self) -> None:
        for callback in self._refresh_callbacks:
            callback()

    def get_work_item(self, item_id: str) -> WorkItem:
        return self.result.work_item_service.get(item_id)


def use_dashboard(todo_service: TodoService, note_service: NoteService, pomodoro_service: PomodoroService, work_item_service: WorkItemService, comment_service: CommentService) -> DashboardHookResult:
    """Create the typed Dashboard business-logic surface used by the view."""

    return DashboardHook(todo_service, note_service, pomodoro_service, work_item_service, comment_service).result
