from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from app.models import WorkItemStatus, WorkItemType
from app.services import WorkItemService
from app.ui.shared.dialogs import ServiceDialog
from app.ui.shared.theme import COLORS
from app.ui.utils import configure_form, format_work_item_type, grid_form_field


class WorkItemDetail(ServiceDialog):
    def __init__(self, parent: tk.Misc, item, work_item_service: WorkItemService, on_saved: Callable[[], None], on_open_item: Callable[[str], None]):
        super().__init__(parent, on_saved)
        self.item = item
        self.work_item_service = work_item_service
        self.on_open_item = on_open_item
        self.title(item.title)
        self.geometry("460x500")
        configure_form(self)
        self._build()

    def _build(self) -> None:
        self.fields = {}
        for row, (label, value) in enumerate((("Title", self.item.title), ("Description", self.item.description))):
            entry = tk.Text(self, height=4, width=38) if label == "Description" else ttk.Entry(self)
            grid_form_field(self, row, label, entry)
            if label == "Description":
                entry.insert("1.0", value)
            else:
                entry.insert(0, value)
            self.fields[label] = entry
        tk.Label(self, text="Type", anchor="w").grid(row=2, column=0, sticky="w", padx=14, pady=10)
        tk.Label(self, text=format_work_item_type(self.item.type), anchor="w").grid(row=2, column=1, sticky="w", padx=(0, 14), pady=10)
        tk.Label(self, text="Status", anchor="w").grid(row=3, column=0, sticky="w", padx=14, pady=10)
        self.status = ttk.Combobox(self, state="readonly", values=[value.value for value in WorkItemStatus])
        self.status.set(self.item.status.value)
        self.status.grid(row=3, column=1, sticky="ew", padx=(0, 14), pady=10)
        next_row = self._build_parent_section(4)
        next_row = self._build_children_section(next_row)
        ttk.Button(self, text="Delete", command=self.on_delete_work_item).grid(row=next_row, column=0, sticky="w", padx=14, pady=18)
        ttk.Button(self, text="Save", command=self.on_save_work_item).grid(row=next_row, column=1, sticky="e", padx=14, pady=18)

    def _build_parent_section(self, row: int) -> int:
        if not self.item.parent_id:
            return row
        parent = self.work_item_service.get(self.item.parent_id)
        tk.Label(self, text="Parent", anchor="w").grid(row=row, column=0, sticky="w", padx=14, pady=10)
        tk.Button(self, text=f"{format_work_item_type(parent.type)}: {parent.title}", anchor="w", relief="flat", borderwidth=0, bg=COLORS["surface"], fg=COLORS["accent"], cursor="hand2", wraplength=300, justify="left", command=lambda: self._open_related(parent.id)).grid(row=row, column=1, sticky="ew", padx=(0, 14), pady=10)
        return row + 1

    def _build_children_section(self, row: int) -> int:
        if self.item.type == WorkItemType.FEATURE:
            child_label = "User Stories"
        elif self.item.type == WorkItemType.USER_STORY:
            child_label = "Tasks"
        else:
            return row

        children = self.work_item_service.get_children(self.item.id)
        completed = sum(child.status in {WorkItemStatus.RESOLVED, WorkItemStatus.CLOSED} for child in children)
        tk.Label(self, text=f"{child_label} {completed}/{len(children)}", anchor="w", font=("Segoe UI", 9, "bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 4))
        for offset, child in enumerate(children, start=1):
            tk.Button(self, text=child.title, anchor="w", relief="flat", borderwidth=0, bg=COLORS["surface"], fg=COLORS["accent"], cursor="hand2", command=lambda child_id=child.id: self._open_related(child_id)).grid(row=row + offset, column=1, sticky="ew", padx=(14, 14), pady=2)
        return row + len(children) + 1

    def _open_related(self, item_id: str) -> None:
        self.destroy()
        self.on_open_item(item_id)

    def on_save_work_item(self) -> None:
        try:
            self.work_item_service.update(self.item.id, {"title": self.fields["Title"].get(), "description": self.fields["Description"].get("1.0", "end-1c")})
            if self.status.get() != self.item.status.value:
                self.work_item_service.move(self.item.id, self.status.get())
        except ValueError as error:
            messagebox.showerror("Cannot update work item", str(error), parent=self)
            return
        self.finish_save()

    def on_delete_work_item(self) -> None:
        if not messagebox.askyesno("Delete work item", f'Delete "{self.item.title}"?', parent=self):
            return
        try:
            self.work_item_service.delete(self.item.id)
        except ValueError as error:
            messagebox.showerror("Cannot delete work item", str(error), parent=self)
            return
        self.finish_save()
