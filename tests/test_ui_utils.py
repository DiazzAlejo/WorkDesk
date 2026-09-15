import unittest
from datetime import datetime, timezone

from app.models import Priority, WorkItem, WorkItemStatus, WorkItemType
from app.ui.features.work_items.work_item_tree import visible_items
from app.ui.utils import format_duration, format_priority, format_work_item_type
from app.ui.hooks import DebounceHook


class UiUtilityTests(unittest.TestCase):
    def test_debouncer_replaces_and_flushes_scheduled_callback(self):
        class Scheduler:
            def __init__(self):
                self.next_id = 0
                self.cancelled = []

            def after(self, _delay, _callback):
                self.next_id += 1
                return f"job-{self.next_id}"

            def after_cancel(self, job):
                self.cancelled.append(job)

        scheduler = Scheduler()
        calls = []
        debouncer = DebounceHook(scheduler, 50, lambda: calls.append("saved"))
        debouncer.schedule()
        debouncer.schedule()
        debouncer.flush()
        self.assertEqual(calls, ["saved"])
        self.assertEqual(scheduler.cancelled, ["job-1", "job-2"])

    def test_formatters(self):
        self.assertEqual(format_duration(1500), "25:00")
        self.assertEqual(format_duration(3661), "01:01:01")
        self.assertEqual(format_duration(-1), "00:00")
        self.assertEqual(format_priority(Priority.HIGH), "High priority")
        self.assertEqual(format_work_item_type(WorkItemType.USER_STORY), "User Story")

    def test_visible_items_filters_to_requested_type(self):
        now = datetime(2026, 9, 15, tzinfo=timezone.utc)
        feature = WorkItem(WorkItemType.FEATURE, "Feature", id="feature", created_at=now, updated_at=now)
        story = WorkItem(WorkItemType.USER_STORY, "Story", parent_id="feature", id="story", created_at=now, updated_at=now)
        task = WorkItem(WorkItemType.TASK, "Task", parent_id="story", id="task", created_at=now, updated_at=now)
        result = visible_items([feature, story, task], WorkItemStatus.NEW, WorkItemType.TASK, {"feature", "story"})
        self.assertEqual([item.id for item in result], ["task"])

    def test_visible_items_shows_child_when_parent_is_in_another_status(self):
        now = datetime(2026, 9, 15, tzinfo=timezone.utc)
        story = WorkItem(WorkItemType.USER_STORY, "Story", id="story", status=WorkItemStatus.NEW, created_at=now, updated_at=now)
        task = WorkItem(WorkItemType.TASK, "Task", parent_id="story", id="task", status=WorkItemStatus.ACTIVE, created_at=now, updated_at=now)
        result = visible_items([story, task], WorkItemStatus.ACTIVE, None, set())
        self.assertEqual([item.id for item in result], ["task"])

    def test_visible_items_expands_children_across_status_lanes(self):
        now = datetime(2026, 9, 15, tzinfo=timezone.utc)
        story = WorkItem(WorkItemType.USER_STORY, "Story", id="story", status=WorkItemStatus.NEW, created_at=now, updated_at=now)
        task = WorkItem(WorkItemType.TASK, "Task", parent_id="story", id="task", status=WorkItemStatus.ACTIVE, created_at=now, updated_at=now)
        result = visible_items([story, task], WorkItemStatus.NEW, None, {"story"})
        self.assertEqual([item.id for item in result], ["story", "task"])

    def test_visible_items_recursively_expands_feature_story_and_task(self):
        now = datetime(2026, 9, 15, tzinfo=timezone.utc)
        feature = WorkItem(WorkItemType.FEATURE, "Feature", id="feature", created_at=now, updated_at=now)
        story = WorkItem(WorkItemType.USER_STORY, "Story", parent_id="feature", id="story", created_at=now, updated_at=now)
        task = WorkItem(WorkItemType.TASK, "Task", parent_id="story", id="task", created_at=now, updated_at=now)
        result = visible_items([feature, story, task], WorkItemStatus.NEW, None, {"feature", "story"})
        self.assertEqual([item.id for item in result], ["feature", "story", "task"])


if __name__ == "__main__":
    unittest.main()
