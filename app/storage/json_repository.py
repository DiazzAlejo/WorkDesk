from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Iterable, Optional


class PersistenceError(ValueError):
    """Raised when local DeskOS data cannot be read or written safely."""


def default_data_path() -> Path:
    if getattr(sys, "frozen", False):
        local_app_data = os.environ.get("LOCALAPPDATA")
        base_path = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        return base_path / "WorkDesk" / "deskos.json"
    return Path("data") / "deskos.json"


class JsonRepository:
    """Versioned local storage shared by application services."""

    SCHEMA_VERSION = 1
    BACKUP_COUNT = 3
    COLLECTIONS = ("todos", "notes", "pomodoro_sessions", "work_items", "comments", "documents")

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path) if path else default_data_path()
        self._lock = RLock()
        self._data: Dict[str, Any] = self._empty_data()
        self.load()

    def _empty_data(self) -> Dict[str, Any]:
        return {"schema_version": self.SCHEMA_VERSION, **{name: [] for name in self.COLLECTIONS}}

    def load(self) -> None:
        with self._lock:
            if not self.path.exists():
                self._data = self._empty_data()
                return
            try:
                with self.path.open("r", encoding="utf-8") as handle:
                    loaded = json.load(handle)
            except (OSError, json.JSONDecodeError) as error:
                raise PersistenceError(f"Unable to read DeskOS data: {self.path}") from error
            if not isinstance(loaded, dict):
                raise PersistenceError("DeskOS data must contain a JSON object")
            if loaded.get("schema_version") != self.SCHEMA_VERSION:
                raise ValueError("Unsupported DeskOS data schema")
            self._data = self._empty_data()
            for name in self.COLLECTIONS:
                collection = loaded.get(name, [])
                if not isinstance(collection, list) or not all(isinstance(record, dict) for record in collection):
                    raise PersistenceError(f"DeskOS collection '{name}' must contain JSON objects")
                self._data[name] = collection

    def save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(prefix="deskos-", suffix=".json", dir=self.path.parent)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(self._data, handle, indent=2)
                self._rotate_backups()
                # Replace only after the complete document is written so a crash cannot leave partial JSON.
                os.replace(temporary, self.path)
            except OSError as error:
                raise PersistenceError(f"Unable to save DeskOS data: {self.path}") from error
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)

    def _rotate_backups(self) -> None:
        if not self.path.exists():
            return
        for backup_number in range(self.BACKUP_COUNT - 1, 0, -1):
            source = self._backup_path(backup_number)
            destination = self._backup_path(backup_number + 1)
            if source.exists():
                os.replace(source, destination)
        shutil.copy2(self.path, self._backup_path(1))

    def _backup_path(self, backup_number: int) -> Path:
        suffix = ".bak" if backup_number == 1 else f".bak.{backup_number - 1}"
        return self.path.with_name(f"{self.path.name}{suffix}")

    def list(self, collection: str) -> list[Dict[str, Any]]:
        self._validate_collection(collection)
        with self._lock:
            return [dict(serialized_record) for serialized_record in self._data[collection]]

    def get(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        self._validate_collection(collection)
        return next((serialized_record for serialized_record in self.list(collection) if serialized_record["id"] == item_id), None)

    def upsert(self, collection: str, serialized_record: Dict[str, Any]) -> None:
        self._validate_collection(collection)
        with self._lock:
            records = self._data[collection]
            for index, current in enumerate(records):
                if current["id"] == serialized_record["id"]:
                    records[index] = dict(serialized_record)
                    self.save()
                    return
            records.append(dict(serialized_record))
            self.save()

    def delete(self, collection: str, item_id: str) -> None:
        self._validate_collection(collection)
        with self._lock:
            self._data[collection] = [serialized_record for serialized_record in self._data[collection] if serialized_record["id"] != item_id]
            self.save()

    def replace(self, collection: str, items: Iterable[Dict[str, Any]]) -> None:
        self._validate_collection(collection)
        with self._lock:
            self._data[collection] = [dict(serialized_record) for serialized_record in items]
            self.save()

    def _validate_collection(self, collection: str) -> None:
        if collection not in self.COLLECTIONS:
            raise ValueError(f"Unknown DeskOS collection: {collection}")
