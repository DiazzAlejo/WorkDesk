import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import Optional

from app.services import CommentService, NoteService, PomodoroService, TodoService, WorkItemService
from app.storage import JsonRepository, PersistenceError
from app.ui import Dashboard


def build_application(root: tk.Tk, data_path: Optional[Path] = None) -> Dashboard:
    repository = JsonRepository(data_path)
    work_items = WorkItemService(repository)
    dashboard = Dashboard(
        root,
        todo_service=TodoService(repository),
        note_service=NoteService(repository),
        pomodoro_service=PomodoroService(repository, work_items),
        work_item_service=work_items,
        comment_service=CommentService(repository, work_items),
    )
    dashboard.pack(fill="both", expand=True)
    return dashboard


def main() -> None:
    root = tk.Tk()
    root.title("WorkDesk")
    root.geometry("1280x760")
    root.minsize(940, 620)
    try:
        build_application(root)
    except PersistenceError as error:
        messagebox.showerror("Unable to open WorkDesk data", str(error), parent=root)
        root.destroy()
        return
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()
