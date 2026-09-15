from __future__ import annotations

import tkinter as tk
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app.main import build_application
from app.ui.features.dashboard import Dashboard


class TkinterTestCase(unittest.TestCase):
    """Own a hidden Tk root and provide deterministic event-loop cleanup."""

    root: tk.Tk
    data_directory: TemporaryDirectory
    dashboard: Dashboard
    data_path: Path

    def setUp(self) -> None:
        self.data_directory = TemporaryDirectory()
        self.data_path = Path(self.data_directory.name) / "deskos.json"
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.data_directory.cleanup()
            self.skipTest(f"Tk runtime unavailable: {error}")
        self.root.withdraw()
        self.dashboard = build_application(self.root, self.data_path)
        self.pump_events()

    def tearDown(self) -> None:
        if self.root.winfo_exists():
            self.root.destroy()
        self.data_directory.cleanup()

    def pump_events(self) -> None:
        self.root.update_idletasks()
        self.root.update()
