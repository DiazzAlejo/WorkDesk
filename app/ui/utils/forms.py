from __future__ import annotations

import tkinter as tk


def configure_form(parent: tk.Misc) -> None:
    """Give the value column of a two-column form the remaining width."""
    parent.columnconfigure(1, weight=1)


def grid_form_field(parent: tk.Misc, row: int, label: str, widget: tk.Widget) -> tk.Widget:
    """Place one labeled control using the shared dialog form spacing."""
    tk.Label(parent, text=label, anchor="w").grid(row=row, column=0, sticky="nw", padx=14, pady=10)
    widget.grid(row=row, column=1, sticky="ew", padx=(0, 14), pady=10)
    return widget
