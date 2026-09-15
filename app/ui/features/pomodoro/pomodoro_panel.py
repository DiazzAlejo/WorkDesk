from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from app.services import PomodoroService
from app.ui.shared.components import SectionFrame
from app.ui.shared.theme import COLORS, FONTS, muted_label_options, surface_frame_options
from app.ui.utils import format_duration
from app.ui.hooks import PomodoroHook


class PomodoroPanel(SectionFrame):
    def __init__(self, parent: tk.Misc, pomodoro_service: PomodoroService):
        super().__init__(parent, "FOCUS")
        self._build()
        self.controller = PomodoroHook(self, pomodoro_service, self.on_pomodoro_state_change)

    def _build(self) -> None:
        self.timer_label = tk.Label(self, text="25:00", **surface_frame_options(fg=COLORS["accent_dark"], font=FONTS["timer"]))
        self.timer_label.pack(anchor="w")
        duration_row = tk.Frame(self, **surface_frame_options())
        duration_row.pack(fill="x", pady=(0, 8))
        tk.Label(duration_row, text="Duration", **muted_label_options()).pack(side="left")
        self.hours_picker = ttk.Combobox(duration_row, state="readonly", width=3, values=[f"{hour:02d}" for hour in range(24)])
        self.hours_picker.set("00")
        self.hours_picker.pack(side="left", padx=(8, 2))
        tk.Label(duration_row, text=":", **muted_label_options()).pack(side="left")
        self.minutes_picker = ttk.Combobox(duration_row, state="readonly", width=3, values=[f"{minute:02d}" for minute in range(60)])
        self.minutes_picker.set("25")
        self.minutes_picker.pack(side="left", padx=(2, 0))
        controls = tk.Frame(self, **surface_frame_options())
        controls.pack(fill="x")
        self.start_button = ttk.Button(controls, text="Start", command=self.on_start_pomodoro)
        self.start_button.pack(side="left")
        ttk.Button(controls, text="Reset", command=self.on_reset_pomodoro).pack(side="left", padx=6)
        self.status_label = tk.Label(self, text="Ready for a focused block", **muted_label_options())
        self.status_label.pack(anchor="w", pady=(8, 0))

    def on_start_pomodoro(self) -> None:
        try:
            hours = int(self.hours_picker.get())
            minutes = int(self.minutes_picker.get())
            duration_seconds = (hours * 60 + minutes) * 60
            if duration_seconds <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid duration", "Choose a duration greater than zero.", parent=self)
            return
        if self.controller.session_id:
            self.controller.pause()
        else:
            self.controller.start(duration_seconds, None)

    def on_reset_pomodoro(self) -> None:
        self.controller.reset()

    def on_pomodoro_state_change(self, state: str, remaining_seconds: int) -> None:
        if state == "ready":
            self.timer_label.config(text="25:00")
            self.start_button.config(text="Start", command=self.on_start_pomodoro)
            self.status_label.config(text="Ready for a focused block")
        elif state == "paused":
            self.timer_label.config(text=format_duration(remaining_seconds))
            self.start_button.config(text="Resume", command=self.controller.resume)
            self.status_label.config(text="Paused")
        elif state == "complete":
            self.timer_label.config(text="00:00")
            self.start_button.config(text="Start", command=self.on_start_pomodoro)
            self.status_label.config(text="Complete")
        else:
            self.timer_label.config(text=format_duration(remaining_seconds))
            self.start_button.config(text="Pause", command=self.controller.pause)
            self.status_label.config(text="In focus")
