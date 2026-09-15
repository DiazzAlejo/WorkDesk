from __future__ import annotations

from app.models import Priority, WorkItemType


def format_duration(seconds: int) -> str:
    """Format a non-negative duration with hours only when needed."""
    total_seconds = max(seconds, 0)
    hours, remaining_seconds = divmod(total_seconds, 3600)
    minutes, remaining_seconds = divmod(remaining_seconds, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"
    return f"{minutes:02d}:{remaining_seconds:02d}"


def format_work_item_type(item_type: WorkItemType) -> str:
    """Convert a stable WorkItem enum value into user-facing title text."""
    return item_type.value.replace("_", " ").title()


def format_priority(priority: Priority) -> str:
    """Convert a priority enum value into the compact card label."""
    return f"{priority.value.title()} priority"
