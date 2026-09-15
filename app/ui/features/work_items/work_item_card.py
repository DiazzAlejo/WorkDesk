from __future__ import annotations

import tkinter as tk
from typing import Callable

from app.ui.shared.theme import COLORS, FONTS, flat_button_options, surface_frame_options
from app.ui.utils import format_work_item_type


class WorkItemCard(tk.Frame):
    """Presentation and pointer events for one WorkItem card."""

    def __init__(self, parent: tk.Misc, work_item, is_expanded: bool, on_open_work_item: Callable[[str, int, int], None], on_start_drag_item: Callable[[str, int, int], None], on_toggle_item_expansion: Callable[[str], None]):
        super().__init__(parent, **surface_frame_options(padx=9, pady=8, cursor="hand2"))
        self.work_item = work_item
        self.on_open_work_item = on_open_work_item
        self.on_start_drag_item = on_start_drag_item
        self.on_toggle_item_expansion = on_toggle_item_expansion
        self._build(is_expanded)

    def _build(self, is_expanded: bool) -> None:
        self.pack(fill="x", pady=4)
        type_label = format_work_item_type(self.work_item.type)
        type_colors = {"FEATURE": COLORS["feature"], "USER_STORY": COLORS["user_story"], "TASK": COLORS["task"]}
        type_row = tk.Frame(self, **surface_frame_options())
        type_row.pack(anchor="w", fill="x")
        tk.Label(type_row, text=type_label, bg=type_colors[self.work_item.type.value], fg=COLORS["ink"], font=FONTS["card_type"], padx=5, pady=2).pack(side="left")
        if self.work_item.child_total:
            tk.Label(type_row, text=f"{self.work_item.child_completed}/{self.work_item.child_total}", **surface_frame_options(fg=COLORS["muted"], font=FONTS["card_meta"])).pack(side="left", padx=(7, 0))
        title_row = tk.Frame(self, **surface_frame_options())
        title_row.pack(fill="x")
        if self.work_item.has_children:
            self.expander = tk.Button(title_row, text="v" if is_expanded else ">", **flat_button_options(), command=lambda: self.on_toggle_item_expansion(self.work_item.id))
            self.expander.pack(side="left")
        self.title_label = tk.Label(title_row, text=self.work_item.title, **surface_frame_options(fg=COLORS["ink"], wraplength=190, justify="left", font=FONTS["card_title"]))
        self.title_label.pack(side="left", fill="x", expand=True)
        self.bind("<Configure>", self._resize_title)
        self._bind_pointer_events()

    def _resize_title(self, event) -> None:
        self.title_label.configure(wraplength=max(140, event.width - 28))

    def _bind_pointer_events(self) -> None:
        def bind_widget(widget: tk.Misc) -> None:
            if widget is getattr(self, "expander", None):
                return
            widget.bind("<ButtonPress-1>", lambda event: self.on_start_drag_item(self.work_item.id, event.x_root, event.y_root))
            widget.bind("<ButtonRelease-1>", lambda event: self.on_open_work_item(self.work_item.id, event.x_root, event.y_root))
            for child in widget.winfo_children():
                bind_widget(child)

        bind_widget(self)


class CardItemAdapter:
    """Adds view-only metadata without changing the WorkItem domain model."""

    def __init__(self, item, children):
        self._item = item
        self.child_total = len(children)
        self.child_completed = sum(child.status.value in {"RESOLVED", "CLOSED"} for child in children)
        self.has_children = self.child_total > 0

    def __getattr__(self, name):
        return getattr(self._item, name)
