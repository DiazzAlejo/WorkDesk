from __future__ import annotations

import tkinter as tk
from typing import Callable
from tkinter import ttk

from app.ui.shared.theme import COLORS, FONTS


class DashboardHeader(tk.Frame):
    def __init__(self, parent: tk.Misc, on_add_work_item: Callable[[], None]):
        super().__init__(parent, bg=COLORS["ink"], padx=24, pady=18)
        self.grid(row=0, column=0, columnspan=3, sticky="ew")
        tk.Label(self, text="WORKDESK", bg=COLORS["ink"], fg="white", font=FONTS["brand"]).pack(side="left")
        ttk.Button(self, text="+ Work Item", command=on_add_work_item).pack(side="right")
