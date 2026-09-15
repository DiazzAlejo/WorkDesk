from __future__ import annotations

from dataclasses import dataclass

from app.models import WorkItemStatus
from app.ui.shared.theme import COLORS


@dataclass(frozen=True)
class StatusColumnConfig:
    label: str
    status: WorkItemStatus
    color: str


STATUS_COLUMNS = (
    StatusColumnConfig("NEW", WorkItemStatus.NEW, COLORS["new"]),
    StatusColumnConfig("ACTIVE", WorkItemStatus.ACTIVE, COLORS["active"]),
    StatusColumnConfig("ON HOLD", WorkItemStatus.ON_HOLD, COLORS["hold"]),
    StatusColumnConfig("RESOLVED", WorkItemStatus.RESOLVED, COLORS["resolved"]),
    StatusColumnConfig("CLOSED", WorkItemStatus.CLOSED, COLORS["closed"]),
)
