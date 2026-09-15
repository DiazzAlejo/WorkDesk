from __future__ import annotations

import tkinter as tk

from app.services import CommentService, NoteService, PomodoroService, TodoService, WorkItemService
from app.ui.hooks import DashboardRefreshers, use_dashboard
from app.ui.features.notes import NotesPanel
from app.ui.features.pomodoro import PomodoroPanel
from app.ui.features.todos import TodoPanel
from app.ui.features.work_items import WorkBoard, WorkItemDetail, WorkItemDialog
from app.ui.shared.theme import COLORS


class Dashboard(tk.Frame):
    def __init__(self, master: tk.Misc, todo_service: TodoService, note_service: NoteService, pomodoro_service: PomodoroService, work_item_service: WorkItemService, comment_service: CommentService):
        super().__init__(master, bg=COLORS["background"])
        self.dashboard = use_dashboard(todo_service, note_service, pomodoro_service, work_item_service, comment_service)
        self._build()
        self.dashboard.register_refreshers(DashboardRefreshers(todos=self.todo_panel.refresh, notes=self.notes_panel.refresh, work_board=self.work_board.refresh))
        self.dashboard.refresh_all()
        self._root = self.winfo_toplevel()
        self._control_n_binding = self._root.bind("<Control-n>", lambda _event: self.on_add_work_item(), add="+")

    def destroy(self) -> None:
        if getattr(self, "_control_n_binding", None):
            self._root.unbind("<Control-n>", self._control_n_binding)
        super().destroy()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=0, minsize=280)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=280)
        self.grid_rowconfigure(0, weight=1)
        self._build_personal_workspace()
        self._build_board()

    def _build_personal_workspace(self) -> None:
        panel = tk.Frame(self, bg=COLORS["background"], padx=14, pady=14)
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        self.pomodoro_panel = PomodoroPanel(panel, self.dashboard.pomodoro_service)
        self.pomodoro_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 12))
        self.notes_panel = NotesPanel(panel, self.dashboard.note_service)
        self.notes_panel.grid(row=1, column=0, sticky="nsew")

        self.todo_panel = TodoPanel(self, self.dashboard.todo_service)
        self.todo_panel.grid(row=0, column=2, sticky="nsew", padx=14, pady=14)

    def _build_board(self) -> None:
        self.work_board = WorkBoard(self, self.dashboard.work_item_service, self.on_open_work_item, self.on_add_work_item)
        self.work_board.grid(row=0, column=1, sticky="nsew")

    def on_add_work_item(self) -> None:
        WorkItemDialog(self, self.dashboard.work_item_service, self.dashboard.refresh_all)

    def on_open_work_item(self, item_id: str) -> None:
        item = self.dashboard.get_work_item(item_id)
        WorkItemDetail(self, item, self.dashboard.work_item_service, self.dashboard.refresh_all, self.on_open_work_item)
