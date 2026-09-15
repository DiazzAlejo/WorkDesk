from __future__ import annotations

import tkinter as tk
from typing import Callable

from app.ui.shared.theme import COLORS, FONTS, flat_button_options, muted_label_options, surface_frame_options
from app.ui.types import ItemCallback, TodoEditCallback


class TodoRow(tk.Frame):
    def __init__(self, parent: tk.Misc, todo, on_toggle_todo: ItemCallback, on_edit_todo: TodoEditCallback, on_delete_todo: ItemCallback):
        super().__init__(parent, **surface_frame_options())
        self.todo = todo
        self._build(on_toggle_todo, on_edit_todo, on_delete_todo)

    def _build(self, on_toggle_todo, on_edit_todo, on_delete_todo) -> None:
        self.pack(fill="x", pady=2)
        check = tk.Canvas(self, width=22, height=22, **surface_frame_options(cursor="hand2"))
        check.pack(side="left", padx=(0, 7))
        fill = COLORS["accent"] if self.todo.completed else COLORS["surface"]
        outline = COLORS["accent"]
        check.create_oval(3, 3, 19, 19, fill=fill, outline=outline, width=2)
        if self.todo.completed:
            check.create_line(7, 11, 10, 14, 16, 8, fill="white", width=2, capstyle="round", joinstyle="round")
        check.bind("<Button-1>", lambda _event: on_toggle_todo(self.todo.id))
        label_options = muted_label_options() if self.todo.completed else surface_frame_options(fg=COLORS["ink"], font=FONTS["body"])
        label = tk.Label(self, text=self.todo.text, anchor="w", **label_options)
        label.pack(side="left", fill="x", expand=True)
        label.bind("<Double-Button-1>", lambda _event: on_edit_todo(self.todo.id, self.todo.text))
        tk.Button(self, text="x", **flat_button_options(fg=COLORS["muted"]), command=lambda: on_delete_todo(self.todo.id)).pack(side="right")
