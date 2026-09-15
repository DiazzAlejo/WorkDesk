COLORS = {
    "background": "#e7edf2",
    "surface": "#ffffff",
    "ink": "#142330",
    "muted": "#526273",
    "line": "#c5d0da",
    "accent": "#087f8c",
    "accent_dark": "#075563",
    "new": "#d5eaf2",
    "active": "#d8eee1",
    "hold": "#f8e8b8",
    "resolved": "#e5e0f4",
    "closed": "#dfe5e9",
    "feature": "#d9c2f0",
    "user_story": "#b9dff2",
    "task": "#c5e8d1",
    "note": "#fff8cc",
    "header_muted": "#b9c8d1",
}

FONTS = {
    "section": ("Segoe UI", 10, "bold"),
    "body": ("Segoe UI", 9),
    "card_type": ("Segoe UI", 8, "bold"),
    "card_meta": ("Segoe UI", 8),
    "card_title": ("Segoe UI", 10, "bold"),
    "timer": ("Segoe UI", 30, "bold"),
    "brand": ("Segoe UI", 18, "bold"),
    "header": ("Segoe UI", 10),
    "board_title": ("Segoe UI", 12, "bold"),
    "column_title": ("Segoe UI", 9, "bold"),
    "note_title": ("Segoe UI", 14, "bold"),
    "note_body": ("Segoe UI", 11),
}


def surface_frame_options(**overrides):
    options = {"bg": COLORS["surface"], "borderwidth": 0, "relief": "flat", "highlightthickness": 0}
    options.update(overrides)
    return options


def surface_label_options(**overrides):
    options = {"bg": COLORS["surface"], "fg": COLORS["ink"], "font": FONTS["body"]}
    options.update(overrides)
    return options


def muted_label_options(**overrides):
    options = surface_label_options(fg=COLORS["muted"])
    options.update(overrides)
    return options


def flat_button_options(**overrides):
    options = {"relief": "flat", "borderwidth": 0, "highlightthickness": 0, "bg": COLORS["surface"], "fg": COLORS["ink"]}
    options.update(overrides)
    return options
