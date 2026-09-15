from __future__ import annotations

import tkinter as tk
from typing import Callable, Iterable

from app.ui.shared.theme import COLORS, FONTS
from .work_item_card import CardItemAdapter, WorkItemCard


class StatusColumn(tk.Frame):
    """A board status lane that renders WorkItem cards and accepts drops."""

    def __init__(self, parent: tk.Misc, label: str, status, color: str, work_items: Iterable, expanded_item_ids: set[str], get_children: Callable[[str], list], on_drop_item: Callable[[object], None], on_open_work_item: Callable[[str, int, int], None], on_start_drag_item: Callable[[str, int, int], None], on_toggle_item_expansion: Callable[[str], None], show_children: bool = True):
        super().__init__(parent, bg=color, width=220, padx=10, pady=10, highlightthickness=0)
        self.grid_propagate(False)
        self.status = status
        self._build(label, color, work_items, expanded_item_ids, get_children, on_drop_item, on_open_work_item, on_start_drag_item, on_toggle_item_expansion, show_children)

    def _build(self, label: str, color: str, work_items: Iterable, expanded_item_ids: set[str], get_children: Callable[[str], list], on_drop_item: Callable[[object], None], on_open_work_item: Callable[[str], None], on_start_drag_item: Callable[[str], None], on_toggle_item_expansion: Callable[[str], None], show_children: bool) -> None:
        tk.Label(self, text=label, bg=color, fg=COLORS["ink"], font=FONTS["column_title"]).pack(anchor="w", pady=(0, 8))
        for work_item in work_items:
            adapted = CardItemAdapter(work_item, get_children(work_item.id) if show_children else [])
            WorkItemCard(self, adapted, work_item.id in expanded_item_ids, on_open_work_item, on_start_drag_item, on_toggle_item_expansion)
