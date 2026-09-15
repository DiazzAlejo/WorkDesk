from __future__ import annotations

from typing import Iterable, Optional

from app.models import WorkItem, WorkItemStatus, WorkItemType


def visible_items(items: Iterable[WorkItem], status: WorkItemStatus, item_type: Optional[WorkItemType], expanded_ids: set[str]) -> list[WorkItem]:
    """Return matching roots and expanded direct children for one board lane."""
    all_items = list(items)
    lane_items = [item for item in all_items if item.status == status]
    if item_type:
        return [item for item in lane_items if item.type == item_type]

    matching_ids = {item.id for item in lane_items if item_type is None or item.type == item_type}
    lane_ids = {item.id for item in lane_items}
    roots = [item for item in lane_items if item.id in matching_ids and (not item.parent_id or item.parent_id not in lane_ids)]
    children_by_parent: dict[str, list[WorkItem]] = {}
    for item in all_items:
        if item.parent_id:
            children_by_parent.setdefault(item.parent_id, []).append(item)

    def append_expanded(item: WorkItem, result: list[WorkItem]) -> None:
        result.append(item)
        if item.id not in expanded_ids:
            return
        for child in children_by_parent.get(item.id, []):
            if item_type is None or child.type == item_type:
                append_expanded(child, result)

    result: list[WorkItem] = []
    for item in roots:
        append_expanded(item, result)
    return result
