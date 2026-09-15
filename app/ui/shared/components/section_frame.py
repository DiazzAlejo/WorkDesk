from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Literal, Optional

from app.ui.shared.theme import COLORS, FONTS, surface_frame_options

SectionVariant = Literal["surface", "muted", "accent"]
SectionSize = Literal["compact", "comfortable"]


@dataclass(frozen=True)
class SectionFrameProps:
    """Typed configuration for a reusable titled panel container."""

    title: str = ""
    variant: SectionVariant = "surface"
    size: SectionSize = "comfortable"
    show_title: bool = True
    title_color: Optional[str] = None


class SectionFrame(tk.Frame):
    """Reusable panel surface with typed visual variations."""

    _VARIANT_COLORS = {
        "surface": (COLORS["surface"], COLORS["line"], COLORS["ink"]),
        "muted": (COLORS["background"], COLORS["line"], COLORS["ink"]),
        "accent": (COLORS["accent_dark"], COLORS["accent_dark"], "white"),
    }
    _SIZE_PADDING = {
        "compact": (10, 8),
        "comfortable": (14, 12),
    }

    def __init__(self, parent: tk.Misc, title: str = "", *, variant: SectionVariant = "surface", size: SectionSize = "comfortable", show_title: bool = True, title_color: Optional[str] = None):
        self.props = SectionFrameProps(title=title, variant=variant, size=size, show_title=show_title, title_color=title_color)
        background, border, default_title_color = self._VARIANT_COLORS[variant]
        padx, pady = self._SIZE_PADDING[size]
        super().__init__(parent, **surface_frame_options(bg=background, highlightbackground=border, highlightthickness=0, padx=padx, pady=pady))
        self.title_row = tk.Frame(self, **surface_frame_options(bg=background))
        if show_title:
            self.title_row.pack(fill="x", pady=(0, 10 if size == "comfortable" else 6))
            tk.Label(self.title_row, text=title, bg=background, fg=title_color or default_title_color, font=FONTS["section"]).pack(side="left")
