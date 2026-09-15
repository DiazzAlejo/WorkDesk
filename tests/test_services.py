import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.models import Priority, WorkItemStatus, WorkItemType
from app.services import CommentService, NoteService, PomodoroService, TodoService, WorkItemService
from app.storage import JsonRepository


class Clock:
    def __init__(self):
        self.current = datetime(2026, 9, 15, 9, tzinfo=timezone.utc)

    def __call__(self):
        return self.current

    def advance(self, **kwargs):
        self.current += timedelta(**kwargs)


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.repository = JsonRepository(Path(self.directory.name) / "deskos.json")
        self.clock = Clock()
        self.work_items = WorkItemService(self.repository, self.clock)
        self.todos = TodoService(self.repository, self.clock)
        self.notes = NoteService(self.repository, self.clock)
        self.pomodoros = PomodoroService(self.repository, self.work_items, self.clock)
        self.comments = CommentService(self.repository, self.work_items, self.clock)

    def tearDown(self):
        self.directory.cleanup()

    def test_todo_completion_and_next_day_visibility(self):
        todo = self.todos.create("Send report")
        self.todos.complete(todo.id)
        visible = self.todos.list()
        self.assertEqual([item.id for item in visible], [todo.id])
        self.assertTrue(visible[0].completed)
        self.clock.advance(days=1)
        self.assertEqual(self.todos.list(), [])
        self.assertEqual(len(self.todos.list(include_completed_history=True)), 1)

    def test_todo_reorder(self):
        first = self.todos.create("First")
        second = self.todos.create("Second")
        self.todos.reorder([second.id, first.id])
        self.assertEqual([item.id for item in self.todos.list()], [second.id, first.id])

    def test_note_update_changes_timestamp(self):
        note = self.notes.create("Ideas", "Initial")
        self.assertEqual(self.notes.get(note.id).id, note.id)
        self.clock.advance(minutes=1)
        updated = self.notes.update(note.id, "Ideas", "Updated")
        self.assertEqual(updated.content, "Updated")
        self.assertGreater(updated.updated_at, note.updated_at)

    def test_notes_list_keeps_new_notes_at_the_back(self):
        first = self.notes.create("First")
        self.clock.advance(minutes=1)
        second = self.notes.create("Second")
        self.notes.update(first.id, "First edited", "Updated")
        self.assertEqual([note.id for note in self.notes.list()], [first.id, second.id])

    def test_pomodoro_defaults_and_work_item_association(self):
        feature = self.work_items.create(WorkItemType.FEATURE, "Release")
        session = self.pomodoros.start(work_item_id=feature.id)
        self.assertEqual(session.duration_seconds, 1500)
        self.assertEqual(session.work_item_id, feature.id)
        self.clock.advance(minutes=25)
        completed = self.pomodoros.complete(session.id)
        self.assertTrue(completed.completed)
        self.assertEqual(len(self.pomodoros.list_history()), 1)

    def test_todo_get_returns_created_record(self):
        todo = self.todos.create("Lookup")
        self.assertEqual(self.todos.get(todo.id).text, "Lookup")

    def test_work_item_hierarchy_and_independent_status(self):
        feature = self.work_items.create(WorkItemType.FEATURE, "Authentication")
        story = self.work_items.create(WorkItemType.USER_STORY, "Login", parent_id=feature.id)
        task = self.work_items.create(WorkItemType.TASK, "Add endpoint", parent_id=story.id)
        self.work_items.move(feature.id, WorkItemStatus.ACTIVE)
        self.assertEqual(self.work_items.get(feature.id).status, WorkItemStatus.ACTIVE)
        self.assertEqual(self.work_items.get(story.id).status, WorkItemStatus.ACTIVE)
        self.assertEqual(self.work_items.get(task.id).status, WorkItemStatus.ACTIVE)
        self.assertEqual([item.id for item in self.work_items.get_children(story.id)], [task.id])

    def test_parent_cannot_resolve_or_close_with_incomplete_descendants(self):
        feature = self.work_items.create(WorkItemType.FEATURE, "Authentication")
        story = self.work_items.create(WorkItemType.USER_STORY, "Login", parent_id=feature.id)
        task = self.work_items.create(WorkItemType.TASK, "Add endpoint", parent_id=story.id)
        with self.assertRaises(ValueError):
            self.work_items.move(story.id, WorkItemStatus.RESOLVED)
        self.work_items.move(task.id, WorkItemStatus.CLOSED)
        self.assertEqual(self.work_items.get(story.id).status, WorkItemStatus.RESOLVED)
        self.assertEqual(self.work_items.get(feature.id).status, WorkItemStatus.RESOLVED)
        self.work_items.move(feature.id, WorkItemStatus.CLOSED)

    def test_children_require_active_parent_to_start_and_resolution_rolls_up(self):
        feature = self.work_items.create(WorkItemType.FEATURE, "Authentication")
        story = self.work_items.create(WorkItemType.USER_STORY, "Login", parent_id=feature.id)
        task = self.work_items.create(WorkItemType.TASK, "Add endpoint", parent_id=story.id)
        with self.assertRaises(ValueError):
            self.work_items.move(story.id, WorkItemStatus.ACTIVE)
        self.work_items.move(feature.id, WorkItemStatus.ACTIVE)
        self.work_items.move(story.id, WorkItemStatus.ACTIVE)
        self.work_items.move(task.id, WorkItemStatus.ACTIVE)
        self.work_items.move(task.id, WorkItemStatus.RESOLVED)
        self.assertEqual(self.work_items.get(story.id).status, WorkItemStatus.RESOLVED)
        self.assertEqual(self.work_items.get(feature.id).status, WorkItemStatus.RESOLVED)

    def test_direct_status_updates_use_hierarchy_rules(self):
        feature = self.work_items.create(WorkItemType.FEATURE, "Authentication")
        story = self.work_items.create(WorkItemType.USER_STORY, "Login", parent_id=feature.id)
        with self.assertRaises(ValueError):
            self.work_items.update(story.id, {"status": WorkItemStatus.ACTIVE})
        with self.assertRaises(ValueError):
            self.work_items.update(story.id, {"id": "changed"})

    def test_closed_parent_locks_child_changes(self):
        feature = self.work_items.create(WorkItemType.FEATURE, "Authentication")
        story = self.work_items.create(WorkItemType.USER_STORY, "Login", parent_id=feature.id)
        self.work_items.move(story.id, WorkItemStatus.CLOSED)
        self.work_items.move(feature.id, WorkItemStatus.CLOSED)
        with self.assertRaises(ValueError):
            self.work_items.move(story.id, WorkItemStatus.ACTIVE)
        with self.assertRaises(ValueError):
            self.work_items.create(WorkItemType.USER_STORY, "Signup", parent_id=feature.id)

    def test_parents_cannot_be_deleted_with_children(self):
        feature = self.work_items.create(WorkItemType.FEATURE, "Authentication")
        story = self.work_items.create(WorkItemType.USER_STORY, "Login", parent_id=feature.id)
        task = self.work_items.create(WorkItemType.TASK, "Add endpoint", parent_id=story.id)
        with self.assertRaisesRegex(ValueError, "Feature with User Stories"):
            self.work_items.delete(feature.id)
        with self.assertRaisesRegex(ValueError, "User Story with Tasks"):
            self.work_items.delete(story.id)
        self.work_items.delete(task.id)
        self.work_items.delete(story.id)
        self.work_items.delete(feature.id)

    def test_work_item_type_filter(self):
        feature = self.work_items.create(WorkItemType.FEATURE, "Authentication")
        self.work_items.create(WorkItemType.USER_STORY, "Login", parent_id=feature.id)
        features = self.work_items.list({"type": WorkItemType.FEATURE})
        self.assertEqual([item.title for item in features], ["Authentication"])

    def test_invalid_work_item_hierarchy(self):
        with self.assertRaises(ValueError):
            self.work_items.create(WorkItemType.USER_STORY, "Orphan story")
        with self.assertRaises(ValueError):
            self.work_items.create(WorkItemType.TASK, "Orphan task")
        feature = self.work_items.create(WorkItemType.FEATURE, "Feature")
        with self.assertRaises(ValueError):
            self.work_items.create(WorkItemType.TASK, "Wrong parent", parent_id=feature.id)

    def test_comment_association_and_update(self):
        feature = self.work_items.create(WorkItemType.FEATURE, "Feature")
        comment = self.comments.create(feature.id, "Alex", "Looks good")
        self.clock.advance(minutes=1)
        updated = self.comments.update(comment.id, "Approved")
        self.assertEqual(self.comments.list_for_work_item(feature.id)[0].content, "Approved")
        self.assertGreater(updated.updated_at, comment.updated_at)


if __name__ == "__main__":
    unittest.main()
