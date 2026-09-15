from __future__ import annotations

import tkinter as tk


def clear_children(parent: tk.Misc) -> None:
    """Remove rendered widgets before a container is repopulated."""
    for child in parent.winfo_children():
        child.destroy()
