from __future__ import annotations

import tkinter as tk
from typing import Callable


class ServiceDialog(tk.Toplevel):
    """Common close/save lifecycle for service-backed dialogs."""

    def __init__(self, parent: tk.Misc, on_saved: Callable[[], None]):
        super().__init__(parent)
        self.on_saved = on_saved
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.after_idle(self.focus_force)

    def finish_save(self) -> None:
        self.on_saved()
        self.destroy()
