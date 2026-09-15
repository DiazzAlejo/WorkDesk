from __future__ import annotations

from typing import Callable, Iterable, TypeVar

import tkinter as tk

from .tkinter_helpers import clear_children


ItemT = TypeVar("ItemT")


def refresh_list(container: tk.Misc, items: Iterable[ItemT], render_item: Callable[[tk.Misc, ItemT], None]) -> None:
    """Replace all rendered children with the current item collection."""
    clear_children(container)
    for item in items:
        render_item(container, item)
