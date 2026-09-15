from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from app.models import WorkItemType
from app.services import WorkItemService
from app.ui.shared.dialogs import ServiceDialog
from app.ui.utils import configure_form, format_work_item_type, grid_form_field


class WorkItemDialog(ServiceDialog):
    def __init__(self, parent: tk.Misc, work_item_service: WorkItemService, on_saved: Callable[[], None]):
        super().__init__(parent, on_saved)
        self.work_item_service = work_item_service
        self.title("New Work Item")
        self.geometry("360x220")
        configure_form(self)
        self._build()

    def _build(self) -> None:
        self.item_type = ttk.Combobox(self, state="readonly", values=["Feature", "User Story", "Task"])
        self.item_type.set("Feature")
        grid_form_field(self, 0, "Type", self.item_type)
        self.item_type.bind("<<ComboboxSelected>>", lambda _event: self._update_parent_choices())
        self.title_entry = ttk.Entry(self)
        grid_form_field(self, 1, "Title", self.title_entry)
        self.parent_label = tk.Label(self, text="Parent", anchor="w")
        self.parent_label.grid(row=2, column=0, sticky="nw", padx=14, pady=10)
        self.parent = ttk.Combobox(self, state="readonly")
        self.parent.grid(row=2, column=1, sticky="ew", padx=(0, 14), pady=10)
        self.parent_values = {}
        self._update_parent_choices()
        ttk.Button(self, text="Create", command=self.on_create_work_item).grid(row=3, column=1, padx=14, pady=16, sticky="e")

    def _update_parent_choices(self) -> None:
        if self.item_type.get() == "Feature":
            self.parent_label.grid_remove()
            self.parent.grid_remove()
            self.parent_values = {"No parent": None}
            self.parent.set("No parent")
            return

        self.parent_label.grid()
        self.parent.grid()
        required_parent_type = WorkItemType.FEATURE if self.item_type.get() == "User Story" else WorkItemType.USER_STORY
        self.parent_values = {
            f"{format_work_item_type(existing.type)}: {existing.title}": existing.id
            for existing in self.work_item_service.list()
            if existing.type == required_parent_type
        }
        choices = list(self.parent_values) or ["No valid parent available"]
        self.parent["values"] = choices
        self.parent.set(choices[0])

    def on_create_work_item(self) -> None:
        type_values = {"Feature": WorkItemType.FEATURE, "User Story": WorkItemType.USER_STORY, "Task": WorkItemType.TASK}
        try:
            self.work_item_service.create(type_values[self.item_type.get()], self.title_entry.get(), parent_id=self.parent_values.get(self.parent.get()))
        except ValueError as error:
            messagebox.showerror("Invalid WorkItem", str(error), parent=self)
            return
        self.finish_save()
