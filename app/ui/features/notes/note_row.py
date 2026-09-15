from __future__ import annotations

import tkinter as tk
from typing import Callable

from app.ui.shared.theme import COLORS, flat_button_options, surface_frame_options


class NoteRow(tk.Frame):
    def __init__(self, parent: tk.Misc, note, on_open_note: Callable[[str], None], on_delete_note: Callable[[str], None]):
        super().__init__(parent, **surface_frame_options())
        self.pack(fill="x", pady=2)
        tk.Button(self, text=note.title, anchor="w", **flat_button_options(), command=lambda: on_open_note(note.id)).pack(side="left", fill="x", expand=True)
        tk.Button(self, text="x", **flat_button_options(fg=COLORS["muted"]), command=lambda: on_delete_note(note.id)).pack(side="right")
