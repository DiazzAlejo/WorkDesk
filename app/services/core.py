from __future__ import annotations

from datetime import date, datetime
from typing import Any, Callable, Dict, Iterable, Optional

from app.models import Comment, Note, PomodoroSession, Priority, Todo, WorkItem, WorkItemStatus, WorkItemType
from app.models.entities import utc_now
from app.storage import JsonRepository


class NotFoundError(ValueError):
    pass


class InvalidHierarchyError(ValueError):
    pass


class TodoService:
    def __init__(self, repository: JsonRepository, clock: Callable[[], datetime] = utc_now) -> None:
        self.repository, self.clock = repository, clock

    def list(self, include_completed_history: bool = False, today: Optional[date] = None) -> list[Todo]:
        """Return active Todos plus same-day completions unless history is requested."""
        today = today or self.clock().date()
        todos = [Todo.from_dict(serialized_todo) for serialized_todo in self.repository.list("todos")]
        if not include_completed_history:
            todos = [todo for todo in todos if not todo.completed or not todo.completed_at or todo.completed_at.date() == today]
        return sorted(todos, key=lambda todo: (todo.completed, todo.position, todo.created_at))

    def create(self, text: str) -> Todo:
        now = self.clock()
        todo = Todo(text=text, position=len(self.repository.list("todos")), created_at=now)
        self.repository.upsert("todos", todo.to_dict())
        return todo

    def update(self, todo_id: str, text: str) -> Todo:
        todo = self._get(todo_id)
        todo.text = text.strip()
        if not todo.text:
            raise ValueError("Todo text is required")
        self.repository.upsert("todos", todo.to_dict())
        return todo

    def get(self, todo_id: str) -> Todo:
        return self._get(todo_id)

    def complete(self, todo_id: str, completed: bool = True) -> Todo:
        todo = self._get(todo_id)
        todo.completed = completed
        todo.completed_at = self.clock() if completed else None
        self.repository.upsert("todos", todo.to_dict())
        return todo

    def delete(self, todo_id: str) -> None:
        self._get(todo_id)
        self.repository.delete("todos", todo_id)

    def reorder(self, todo_ids: Iterable[str]) -> list[Todo]:
        todos = {todo.id: todo for todo in self.list(include_completed_history=True)}
        requested = list(todo_ids)
        if set(requested) != set(todos):
            raise ValueError("Reorder must include every Todo")
        for position, todo_id in enumerate(requested):
            todos[todo_id].position = position
            self.repository.upsert("todos", todos[todo_id].to_dict())
        return self.list(include_completed_history=True)

    def _get(self, todo_id: str) -> Todo:
        serialized_todo = self.repository.get("todos", todo_id)
        if not serialized_todo:
            raise NotFoundError("Todo not found")
        return Todo.from_dict(serialized_todo)


class NoteService:
    def __init__(self, repository: JsonRepository, clock: Callable[[], datetime] = utc_now) -> None:
        self.repository, self.clock = repository, clock

    def list(self) -> list[Note]:
        return sorted((Note.from_dict(serialized_note) for serialized_note in self.repository.list("notes")), key=lambda note: note.created_at)

    def create(self, title: str, content: str = "") -> Note:
        now = self.clock()
        note = Note(title=title, content=content, created_at=now, updated_at=now)
        self.repository.upsert("notes", note.to_dict())
        return note

    def update(self, note_id: str, title: str, content: str) -> Note:
        note = self._get(note_id)
        note.title, note.content, note.updated_at = title.strip(), content, self.clock()
        if not note.title:
            raise ValueError("Note title is required")
        self.repository.upsert("notes", note.to_dict())
        return note

    def get(self, note_id: str) -> Note:
        return self._get(note_id)

    def delete(self, note_id: str) -> None:
        self._get(note_id)
        self.repository.delete("notes", note_id)

    def _get(self, note_id: str) -> Note:
        serialized_note = self.repository.get("notes", note_id)
        if not serialized_note:
            raise NotFoundError("Note not found")
        return Note.from_dict(serialized_note)


class PomodoroService:
    DEFAULT_DURATION_SECONDS = 25 * 60

    def __init__(self, repository: JsonRepository, work_items: Optional["WorkItemService"] = None, clock: Callable[[], datetime] = utc_now) -> None:
        self.repository, self.work_items, self.clock = repository, work_items, clock
        self.active: Dict[str, PomodoroSession] = {}

    def start(self, duration_seconds: int = DEFAULT_DURATION_SECONDS, work_item_id: Optional[str] = None) -> PomodoroSession:
        if duration_seconds <= 0:
            raise ValueError("Duration must be positive")
        if work_item_id and self.work_items:
            self.work_items.get(work_item_id)
        session = PomodoroSession(duration_seconds=duration_seconds, work_item_id=work_item_id, started_at=self.clock())
        self.active[session.id] = session
        return session

    def pause(self, session_id: str) -> PomodoroSession:
        return self._active(session_id)

    def resume(self, session_id: str) -> PomodoroSession:
        return self._active(session_id)

    def reset(self, session_id: str) -> None:
        self.active.pop(session_id, None)

    def complete(self, session_id: str) -> PomodoroSession:
        session = self._active(session_id)
        session.ended_at, session.completed = self.clock(), True
        self.repository.upsert("pomodoro_sessions", session.to_dict())
        self.active.pop(session_id, None)
        return session

    def list_history(self) -> list[PomodoroSession]:
        return [PomodoroSession.from_dict(serialized_session) for serialized_session in self.repository.list("pomodoro_sessions")]

    def _active(self, session_id: str) -> PomodoroSession:
        if session_id not in self.active:
            raise NotFoundError("Active Pomodoro not found")
        return self.active[session_id]


class WorkItemService:
    def __init__(self, repository: JsonRepository, clock: Callable[[], datetime] = utc_now) -> None:
        self.repository, self.clock = repository, clock

    def create(self, work_item_type: WorkItemType, title: str, description: str = "", status: WorkItemStatus = WorkItemStatus.NEW, priority: Priority = Priority.MEDIUM, parent_id: Optional[str] = None, assigned_to: Optional[str] = None) -> WorkItem:
        now = self.clock()
        work_item = WorkItem(type=work_item_type, title=title, description=description, status=status, priority=priority, parent_id=parent_id, assigned_to=assigned_to, created_at=now, updated_at=now)
        self._validate_parent(work_item.type, parent_id, work_item.id)
        if parent_id and work_item.status == WorkItemStatus.ACTIVE:
            self._validate_parent_is_active(parent_id)
        self.repository.upsert("work_items", work_item.to_dict())
        return work_item

    def get(self, work_item_id: str) -> WorkItem:
        serialized_work_item = self.repository.get("work_items", work_item_id)
        if not serialized_work_item:
            raise NotFoundError("Work item not found")
        return WorkItem.from_dict(serialized_work_item)

    def list(self, filters: Optional[Dict[str, Any]] = None) -> list[WorkItem]:
        work_items = [WorkItem.from_dict(serialized_work_item) for serialized_work_item in self.repository.list("work_items")]
        filters = filters or {}
        return [work_item for work_item in work_items if all(getattr(work_item, key, None) == (filter_value if not isinstance(filter_value, EnumLike) else filter_value.value) for key, filter_value in filters.items())]

    def update(self, work_item_id: str, patch: Dict[str, Any]) -> WorkItem:
        item = self.get(work_item_id)
        immutable_fields = {"id", "created_at", "updated_at"}
        forbidden_fields = immutable_fields.intersection(patch)
        if forbidden_fields:
            raise ValueError(f"WorkItem fields cannot be updated: {', '.join(sorted(forbidden_fields))}")
        original_status = item.status
        for field_name, field_value in patch.items():
            if field_name in {"type", "status", "priority"}:
                field_value = {"type": WorkItemType, "status": WorkItemStatus, "priority": Priority}[field_name](field_value)
            if hasattr(item, field_name):
                setattr(item, field_name, field_value)
        if item.status != original_status:
            self._validate_status_change(self.get(work_item_id), item.status)
        self._validate_parent(item.type, item.parent_id, item.id)
        item.updated_at = self.clock()
        self.repository.upsert("work_items", item.to_dict())
        return item

    def delete(self, work_item_id: str) -> None:
        item = self.get(work_item_id)
        if self.get_children(work_item_id):
            if item.type == WorkItemType.FEATURE:
                raise InvalidHierarchyError("Cannot delete a Feature with User Stories")
            if item.type == WorkItemType.USER_STORY:
                raise InvalidHierarchyError("Cannot delete a User Story with Tasks")
            raise InvalidHierarchyError("Cannot delete a WorkItem with children")
        self.repository.delete("work_items", work_item_id)

    def move(self, work_item_id: str, status: WorkItemStatus) -> WorkItem:
        """Move one item while preserving hierarchy state rules and rolling up completion."""
        item = self.get(work_item_id)
        status = WorkItemStatus(status)
        self._validate_status_change(item, status)
        moved = self.update(work_item_id, {"status": status})
        if status == WorkItemStatus.ACTIVE:
            for child in self._descendants(moved.id):
                self.update(child.id, {"status": WorkItemStatus.ACTIVE})
        if status in {WorkItemStatus.RESOLVED, WorkItemStatus.CLOSED}:
            self._roll_up_resolution(moved.parent_id)
        return moved

    def get_children(self, parent_id: str) -> list[WorkItem]:
        return [item for item in self.list() if item.parent_id == parent_id]

    def get_hierarchy(self, filters: Optional[Dict[str, Any]] = None) -> list[WorkItem]:
        return self.list(filters)

    def _descendants(self, parent_id: str) -> list[WorkItem]:
        descendants: list[WorkItem] = []
        pending = list(self.get_children(parent_id))
        while pending:
            child = pending.pop(0)
            descendants.append(child)
            pending.extend(self.get_children(child.id))
        return descendants

    def _validate_status_change(self, item: WorkItem, status: WorkItemStatus) -> None:
        if item.parent_id:
            parent = self.get(item.parent_id)
            if parent.status == WorkItemStatus.CLOSED:
                raise InvalidHierarchyError("Reopen the parent before changing a child")
            if status == WorkItemStatus.ACTIVE and parent.status != WorkItemStatus.ACTIVE:
                raise InvalidHierarchyError("A child can become Active only when its parent is Active")

        if item.type in {WorkItemType.FEATURE, WorkItemType.USER_STORY} and status in {WorkItemStatus.RESOLVED, WorkItemStatus.CLOSED}:
            children = self.get_children(item.id)
            incomplete = [child for child in children if child.status not in {WorkItemStatus.RESOLVED, WorkItemStatus.CLOSED}]
            if incomplete:
                raise InvalidHierarchyError("Resolve or close all child work items first")

    def _validate_parent_is_active(self, parent_id: str) -> None:
        if self.get(parent_id).status != WorkItemStatus.ACTIVE:
            raise InvalidHierarchyError("A child can become Active only when its parent is Active")

    def _roll_up_resolution(self, parent_id: Optional[str]) -> None:
        if not parent_id:
            return
        parent = self.get(parent_id)
        children = self.get_children(parent.id)
        if parent.status != WorkItemStatus.CLOSED and children and all(child.status in {WorkItemStatus.RESOLVED, WorkItemStatus.CLOSED} for child in children):
            self.update(parent.id, {"status": WorkItemStatus.RESOLVED})
            self._roll_up_resolution(parent.parent_id)

    def _validate_parent(self, item_type: WorkItemType, parent_id: Optional[str], item_id: str) -> None:
        if item_type == WorkItemType.FEATURE and parent_id:
            raise InvalidHierarchyError("Features cannot have parents")
        if item_type == WorkItemType.USER_STORY and not parent_id:
            raise InvalidHierarchyError("User Stories require a Feature parent")
        if item_type == WorkItemType.TASK and not parent_id:
            raise InvalidHierarchyError("Tasks require a User Story parent")
        if not parent_id:
            return
        parent = self.get(parent_id)
        expected = WorkItemType.FEATURE if item_type == WorkItemType.USER_STORY else WorkItemType.USER_STORY
        if parent.type != expected:
            raise InvalidHierarchyError(f"{item_type.value} must belong to a {expected.value}")
        if parent.status == WorkItemStatus.CLOSED:
            raise InvalidHierarchyError("Reopen the parent before adding children")
        if parent.id == item_id:
            raise InvalidHierarchyError("A WorkItem cannot be its own parent")


class EnumLike:
    value: str


class CommentService:
    def __init__(self, repository: JsonRepository, work_items: WorkItemService, clock: Callable[[], datetime] = utc_now) -> None:
        self.repository, self.work_items, self.clock = repository, work_items, clock

    def create(self, work_item_id: str, author: str, content: str) -> Comment:
        self.work_items.get(work_item_id)
        now = self.clock()
        comment = Comment(work_item_id=work_item_id, author=author, content=content, created_at=now, updated_at=now)
        self.repository.upsert("comments", comment.to_dict())
        return comment

    def list_for_work_item(self, work_item_id: str) -> list[Comment]:
        self.work_items.get(work_item_id)
        return [Comment.from_dict(item) for item in self.repository.list("comments") if item["work_item_id"] == work_item_id]

    def update(self, comment_id: str, content: str) -> Comment:
        record = self.repository.get("comments", comment_id)
        if not record:
            raise NotFoundError("Comment not found")
        comment = Comment.from_dict(record)
        comment.content, comment.updated_at = content.strip(), self.clock()
        if not comment.content:
            raise ValueError("Comment content is required")
        self.repository.upsert("comments", comment.to_dict())
        return comment
