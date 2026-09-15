from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

from app.services import NoteService
from app.ui.shared.theme import COLORS, FONTS
from app.ui.hooks import DebounceHook


class NoteEditor(tk.Toplevel):
    def __init__(self, parent: tk.Misc, note, note_service: NoteService, on_saved: Optional[Callable[[], None]] = None, on_closed: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.note = note
        self.note_service = note_service
        self.on_saved = on_saved
        self.on_closed = on_closed
        self.debouncer = DebounceHook(self, 650, self.save_note)
        self.title(note.title)
        self.geometry("440x360")
        self.transient(parent)
        self.configure(bg=COLORS["note"])
        self._build()
        self.protocol("WM_DELETE_WINDOW", self.on_close_editor)

    def _build(self) -> None:
        self.title_var = tk.StringVar(value=self.note.title)
        tk.Entry(self, textvariable=self.title_var, relief="flat", bg=COLORS["note"], fg=COLORS["ink"], font=FONTS["note_title"]).pack(fill="x", padx=18, pady=(18, 8))
        self.content = tk.Text(self, relief="flat", bg=COLORS["note"], fg=COLORS["ink"], wrap="word", font=FONTS["note_body"], padx=14, pady=10)
        self.content.pack(fill="both", expand=True, padx=8)
        self.content.insert("1.0", self.note.content)
        self.saved = tk.Label(self, text="Saved", bg=COLORS["note"], fg=COLORS["muted"], font=FONTS["body"])
        self.saved.pack(anchor="w", padx=18, pady=10)
        self.title_var.trace_add("write", lambda *_args: self.on_note_content_change())
        self.content.bind("<KeyRelease>", self.on_note_content_change)

    def on_note_content_change(self, _event=None) -> None:
        self.saved.config(text="Saving...")
        self.debouncer.schedule()

    def save_note(self) -> None:
        try:
            self.note_service.update(self.note.id, self.title_var.get(), self.content.get("1.0", "end-1c"))
        except (OSError, ValueError) as error:
            self.saved.config(text="Not saved")
            messagebox.showerror("Unable to save note", str(error), parent=self)
            return
        self.saved.config(text="Saved")
        if self.on_saved:
            self.on_saved()

    def on_close_editor(self) -> None:
        self.debouncer.flush()
        if self.on_closed:
            self.on_closed()
        self.destroy()
