from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog, ttk

from app.services import NoteService
from app.ui.shared.components import SectionFrame
from app.ui.shared.theme import COLORS, surface_frame_options
from app.ui.utils import refresh_list
from .note_editor import NoteEditor
from .note_row import NoteRow


class NotesPanel(SectionFrame):
    def __init__(self, parent: tk.Misc, note_service: NoteService):
        super().__init__(parent, "NOTES")
        self.note_service = note_service
        self.open_editors = {}
        self._build()

    def _build(self) -> None:
        ttk.Button(self.title_row, text="+ New Note", command=self.on_add_note).pack(side="right")
        self.note_list = tk.Frame(self, **surface_frame_options())
        self.note_list.pack(fill="x")

    def refresh(self) -> None:
        refresh_list(self.note_list, self.note_service.list(), lambda parent, note: NoteRow(parent, note, self.on_open_note, self.on_delete_note))

    def on_add_note(self) -> None:
        title = simpledialog.askstring("New Note", "Title", parent=self)
        if title:
            note = self.note_service.create(title)
            self.refresh()
            self.on_open_note(note.id)

    def on_open_note(self, note_id: str) -> None:
        existing = self.open_editors.get(note_id)
        if existing is not None and existing.winfo_exists():
            existing.deiconify()
            existing.lift()
            existing.focus_force()
            return

        note = self.note_service.get(note_id)
        self.open_editors[note_id] = NoteEditor(
            self,
            note,
            self.note_service,
            self.refresh,
            lambda: self.open_editors.pop(note_id, None),
        )

    def on_delete_note(self, note_id: str) -> None:
        editor = self.open_editors.get(note_id)
        if editor is not None and editor.winfo_exists():
            editor.on_close_editor()
        self.note_service.delete(note_id)
        self.refresh()
