import unittest

from app.ui.types import (
    is_api_response,
    is_note_response,
    is_todo_response,
    is_work_item_response,
)


class ApiTypeGuardTests(unittest.TestCase):
    def test_guards_reject_none_and_non_mappings(self):
        for guard in (is_api_response, is_note_response, is_todo_response, is_work_item_response):
            self.assertFalse(guard(None))
            self.assertFalse(guard([]))
            self.assertFalse(guard("invalid"))

    def test_resource_guards_accept_nullable_fields(self):
        self.assertTrue(is_todo_response({
            "id": "todo-1",
            "text": "Review report",
            "completed": False,
            "created_at": "2026-09-15T09:00:00+00:00",
            "completed_at": None,
            "position": 0,
        }))
        self.assertTrue(is_work_item_response({
            "id": "task-1",
            "type": "TASK",
            "title": "Add validation",
            "description": "",
            "status": "NEW",
            "priority": "MEDIUM",
            "parent_id": None,
            "assigned_to": None,
            "created_at": "2026-09-15T09:00:00+00:00",
            "updated_at": "2026-09-15T09:00:00+00:00",
        }))

    def test_api_response_accepts_nested_collections_and_optional_metadata(self):
        response = {
            "data": {
                "notes": [{
                    "id": "note-1",
                    "title": "Ideas",
                    "content": "Caching",
                    "created_at": "2026-09-15T09:00:00+00:00",
                    "updated_at": "2026-09-15T09:00:00+00:00",
                }],
                "work_items": [],
            },
            "error": None,
            "meta": {"request_id": "request-1", "page": 1, "page_size": 25, "total": 1},
        }
        self.assertTrue(is_api_response(response))
        self.assertTrue(is_api_response({"data": None, "error": {"code": "not_found", "message": "Missing"}}))

    def test_guards_reject_wrong_nested_types_and_boolean_integers(self):
        invalid_todo = {
            "id": "todo-1",
            "text": "Review report",
            "completed": False,
            "created_at": "2026-09-15T09:00:00+00:00",
            "completed_at": None,
            "position": True,
        }
        invalid_response = {"data": {"todos": [invalid_todo]}, "error": None}
        self.assertFalse(is_todo_response(invalid_todo))
        self.assertFalse(is_api_response(invalid_response))


if __name__ == "__main__":
    unittest.main()
