from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog, ttk

from app.services import TodoService
from app.ui.shared.components import SectionFrame
from app.ui.shared.theme import COLORS, surface_frame_options
from app.ui.utils import refresh_list
from .todo_row import TodoRow


class TodoPanel(SectionFrame):
    def __init__(self, parent: tk.Misc, todo_service: TodoService):
        super().__init__(parent, "TO-DO")
        self.todo_service = todo_service
        self._build()

    def _build(self) -> None:
        row = tk.Frame(self, **surface_frame_options())
        row.pack(fill="x", pady=(0, 6))
        self.todo_entry = ttk.Entry(row)
        self.todo_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Add", command=self.on_add_todo).pack(side="left", padx=(6, 0))
        self.todo_entry.bind("<Return>", lambda _event: self.on_add_todo())
        self.todo_list = tk.Frame(self, **surface_frame_options())
        self.todo_list.pack(fill="x")

    def refresh(self) -> None:
        refresh_list(self.todo_list, self.todo_service.list(), lambda parent, todo: TodoRow(parent, todo, self.on_toggle_todo, self.on_edit_todo, self.on_delete_todo))

    def on_add_todo(self) -> None:
        text = self.todo_entry.get().strip()
        if text:
            self.todo_service.create(text)
            self.todo_entry.delete(0, tk.END)
            self.todo_entry.focus_set()
            self.refresh()

    def on_toggle_todo(self, todo_id: str) -> None:
        current = self.todo_service.get(todo_id)
        self.todo_service.complete(todo_id, not current.completed)
        self.refresh()

    def on_edit_todo(self, todo_id: str, text: str) -> None:
        value = simpledialog.askstring("Edit Todo", "Todo", initialvalue=text, parent=self)
        if value:
            self.todo_service.update(todo_id, value)
            self.refresh()

    def on_delete_todo(self, todo_id: str) -> None:
        self.todo_service.delete(todo_id)
        self.refresh()
