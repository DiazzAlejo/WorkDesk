import json
import tempfile
import unittest
from pathlib import Path

from app.storage import JsonRepository


class RepositoryTests(unittest.TestCase):
    def test_round_trip_uses_versioned_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "deskos.json"
            repository = JsonRepository(path)
            repository.upsert("todos", {"id": "todo-1", "text": "Test"})
            loaded = JsonRepository(path)
            self.assertEqual(loaded.get("todos", "todo-1")["text"], "Test")

    def test_malformed_schema_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deskos.json"
            path.write_text('{"schema_version": 99}', encoding="utf-8")
            with self.assertRaises(ValueError):
                JsonRepository(path)

    def test_malformed_json_is_rejected_with_persistence_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deskos.json"
            path.write_text("{not-json", encoding="utf-8")
            with self.assertRaises(ValueError):
                JsonRepository(path)

    def test_malformed_collection_shape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deskos.json"
            path.write_text(json.dumps({"schema_version": 1, "todos": {}}), encoding="utf-8")
            with self.assertRaises(ValueError):
                JsonRepository(path)

    def test_unknown_collection_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = JsonRepository(Path(directory) / "deskos.json")
            with self.assertRaises(ValueError):
                repository.list("unknown")

    def test_save_rotates_previous_primary_into_backups(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deskos.json"
            repository = JsonRepository(path)
            repository.upsert("todos", {"id": "todo-1", "text": "First"})
            repository.upsert("todos", {"id": "todo-1", "text": "Second"})
            repository.upsert("todos", {"id": "todo-1", "text": "Third"})
            repository.upsert("todos", {"id": "todo-1", "text": "Fourth"})

            self.assertEqual(JsonRepository(path).get("todos", "todo-1")["text"], "Fourth")
            self.assertEqual(json.loads(path.with_name("deskos.json.bak").read_text())["todos"][0]["text"], "Third")
            self.assertEqual(json.loads(path.with_name("deskos.json.bak.1").read_text())["todos"][0]["text"], "Second")
            self.assertEqual(json.loads(path.with_name("deskos.json.bak.2").read_text())["todos"][0]["text"], "First")


if __name__ == "__main__":
    unittest.main()
