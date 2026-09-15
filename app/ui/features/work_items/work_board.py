from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional
from tkinter import ttk

from app.models import WorkItemStatus, WorkItemType
from app.services import WorkItemService
from app.ui.shared.theme import COLORS, FONTS
from app.ui.utils import refresh_list
from .status_column import StatusColumn
from .status_config import STATUS_COLUMNS, StatusColumnConfig
from .work_item_tree import visible_items


class WorkBoard(tk.Frame):
    """Engineering board view and its transient interaction state."""

    STATUSES = STATUS_COLUMNS
    FILTER_TYPES = {"Feature": WorkItemType.FEATURE, "User Story": WorkItemType.USER_STORY, "Task": WorkItemType.TASK}

    def __init__(self, parent: tk.Misc, work_item_service: WorkItemService, on_open_item: Callable[[str], None], on_add_item: Callable[[], None]):
        super().__init__(parent, bg=COLORS["background"], padx=0, pady=18)
        self.work_item_service = work_item_service
        self.on_open_item = on_open_item
        self.on_add_item = on_add_item
        self.expanded_item_ids: set[str] = set()
        self.dragged_item_id: Optional[str] = None
        self.drag_start: Optional[tuple[int, int]] = None
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)
        toolbar = tk.Frame(self, bg=COLORS["background"])
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Button(toolbar, text="+ Work Item", command=self.on_add_item).pack(side="right", padx=(8, 0))
        self.work_filter = ttk.Combobox(toolbar, state="readonly", values=("All Work Items", "Feature", "User Story", "Task"), width=18)
        self.work_filter.set("All Work Items")
        self.work_filter.pack(side="right")
        self.work_filter.bind("<<ComboboxSelected>>", lambda _event: self.refresh())
        self.board_canvas = tk.Canvas(self, bg=COLORS["background"], highlightthickness=0)
        self.board_canvas.grid(row=1, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(self, orient="vertical", command=self.board_canvas.yview)
        vertical.grid(row=1, column=1, sticky="ns")
        self.board_canvas.configure(yscrollcommand=vertical.set)
        self.board_inner = tk.Frame(self.board_canvas, bg=COLORS["background"])
        self.board_inner.grid_rowconfigure(0, weight=1)
        self.board_window = self.board_canvas.create_window((0, 0), window=self.board_inner, anchor="nw")
        self.board_inner.bind("<Configure>", lambda _event: self.board_canvas.configure(scrollregion=self.board_canvas.bbox("all")))
        self.board_canvas.bind("<Configure>", self._resize_board_inner)
        self._root = self.winfo_toplevel()
        self._release_binding = self._root.bind("<ButtonRelease-1>", self._on_pointer_release, add="+")

    def destroy(self) -> None:
        if getattr(self, "_release_binding", None):
            self._root.unbind("<ButtonRelease-1>", self._release_binding)
        super().destroy()

    def _resize_board_inner(self, event) -> None:
        content_width = self.board_inner.winfo_reqwidth()
        content_height = self.board_inner.winfo_reqheight()
        self.board_canvas.itemconfigure(
            self.board_window,
            width=max(event.width, content_width),
            height=max(event.height, content_height),
        )

    def refresh(self) -> None:
        def render_column(parent, config: StatusColumnConfig):
            show_children = self.work_filter.get() == "All Work Items"
            column = StatusColumn(parent, config.label, config.status, config.color, self._visible_items(config.status), self.expanded_item_ids, self.work_item_service.get_children, self.on_drop_item, self._on_card_release, self.on_start_drag_item, self.on_toggle_item_expansion, show_children)
            column_index = self.STATUSES.index(config)
            self.board_inner.grid_columnconfigure(column_index, weight=1, uniform="status")
            column.grid(row=0, column=column_index, sticky="nsew", padx=(0, 10))

        refresh_list(self.board_inner, self.STATUSES, render_column)

    def _visible_items(self, status: WorkItemStatus):
        type_filter = self.FILTER_TYPES.get(self.work_filter.get())
        return visible_items(self.work_item_service.list(), status, type_filter, self.expanded_item_ids)

    def on_start_drag_item(self, item_id: str, x_root: int, y_root: int) -> None:
        self.dragged_item_id = item_id
        self.drag_start = (x_root, y_root)

    def _on_card_release(self, item_id: str, x_root: int, y_root: int) -> None:
        if self.drag_start:
            start_x, start_y = self.drag_start
            if abs(x_root - start_x) > 4 or abs(y_root - start_y) > 4:
                return
        self.dragged_item_id = None
        self.drag_start = None
        self.on_open_item(item_id)

    def _on_pointer_release(self, event) -> Optional[str]:
        if not self.dragged_item_id or not self.drag_start:
            return None

        start_x, start_y = self.drag_start
        moved = abs(event.x_root - start_x) > 4 or abs(event.y_root - start_y) > 4
        if not moved:
            self.dragged_item_id = None
            self.drag_start = None
            return None

        target = self.winfo_containing(event.x_root, event.y_root)
        while target is not None:
            if isinstance(target, StatusColumn):
                self.on_drop_item(target.status)
                return "break"
            target = target.master

        self.dragged_item_id = None
        self.drag_start = None
        return None

    def on_drop_item(self, status: WorkItemStatus) -> None:
        if self.dragged_item_id:
            try:
                self.work_item_service.move(self.dragged_item_id, status)
            except ValueError as error:
                messagebox.showerror("Cannot move work item", str(error), parent=self)
            finally:
                self.dragged_item_id = None
                self.drag_start = None
            self.refresh()

    def on_toggle_item_expansion(self, item_id: str) -> None:
        if item_id in self.expanded_item_ids:
            self.expanded_item_ids.remove(item_id)
        else:
            self.expanded_item_ids.add(item_id)
        self.refresh()
