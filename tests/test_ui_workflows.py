from __future__ import annotations

from tests.ui_harness import TkinterTestCase


class DashboardWorkflowTests(TkinterTestCase):
    def test_todo_entry_submits_with_return_key(self):
        todo_entry = self.dashboard.todo_panel.todo_entry
        todo_entry.insert(0, "Review release notes")
        self.assertTrue(todo_entry.bind("<Return>"))
        self.dashboard.todo_panel.on_add_todo()
        self.pump_events()

        todos = self.dashboard.dashboard.todo_service.list(include_completed_history=True)
        self.assertEqual([todo.text for todo in todos], ["Review release notes"])
        self.assertEqual(todo_entry.get(), "")

    def test_dashboard_panels_render_from_empty_storage(self):
        self.assertEqual(self.dashboard.dashboard.todo_service.list(), [])
        self.assertEqual(self.dashboard.dashboard.note_service.list(), [])
        self.assertEqual(self.dashboard.dashboard.work_item_service.list(), [])
        self.assertTrue(self.dashboard.todo_panel.winfo_exists())
        self.assertTrue(self.dashboard.notes_panel.winfo_exists())
        self.assertTrue(self.dashboard.work_board.winfo_exists())
