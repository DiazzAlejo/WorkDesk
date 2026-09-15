"""Shared typed payloads and runtime guards for DeskOS service/API boundaries."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional, TypedDict

try:
    from typing import TypeGuard
except ImportError:  # Python 3.8 and 3.9 compatibility.
    from typing_extensions import TypeGuard


class ApiError(TypedDict, total=False):
    """Structured error returned when an API operation cannot complete."""

    code: str
    message: str
    details: Optional[Mapping[str, object]]


class ApiMeta(TypedDict, total=False):
    """Optional request and pagination metadata attached to an API response."""

    request_id: str
    page: int
    page_size: int
    total: int


class TodoResponse(TypedDict, total=False):
    """Serialized personal Todo returned by a service/API boundary."""

    id: str
    text: str
    completed: bool
    created_at: str
    completed_at: Optional[str]
    position: int


class NoteResponse(TypedDict, total=False):
    """Serialized titled Note returned by a service/API boundary."""

    id: str
    title: str
    content: str
    created_at: str
    updated_at: str


class PomodoroSessionResponse(TypedDict, total=False):
    """Serialized completed or active Pomodoro session."""

    id: str
    work_item_id: Optional[str]
    started_at: Optional[str]
    ended_at: Optional[str]
    duration_seconds: int
    completed: bool


class WorkItemResponse(TypedDict, total=False):
    """Serialized Feature, User Story, or Task response."""

    id: str
    type: str
    title: str
    description: str
    status: str
    priority: str
    parent_id: Optional[str]
    created_at: str
    updated_at: str
    assigned_to: Optional[str]
    tags: list[str]
    due_date: Optional[str]
    estimate: Optional[float]
    created_by: Optional[str]


class CommentResponse(TypedDict, total=False):
    """Serialized comment associated with a WorkItem."""

    id: str
    work_item_id: str
    author: str
    content: str
    created_at: str
    updated_at: str


class ApiPayload(TypedDict, total=False):
    """Nested resource collections returned in the main API response data field."""

    todos: list[TodoResponse]
    notes: list[NoteResponse]
    pomodoro_sessions: list[PomodoroSessionResponse]
    work_items: list[WorkItemResponse]
    comments: list[CommentResponse]
    documents: list[Mapping[str, object]]


class ApiResponse(TypedDict, total=False):
    """Main DeskOS API response envelope with nullable data and error branches."""

    data: Optional[ApiPayload]
    error: Optional[ApiError]
    meta: Optional[ApiMeta]


def _is_mapping(value: object) -> TypeGuard[Mapping[str, object]]:
    return isinstance(value, Mapping)


def _has_string(payload: Mapping[str, object], field_name: str) -> bool:
    return isinstance(payload.get(field_name), str)


def _has_nullable_string(payload: Mapping[str, object], field_name: str) -> bool:
    field_value = payload.get(field_name)
    return field_value is None or isinstance(field_value, str)


def is_api_error(value: object) -> TypeGuard[ApiError]:
    """Return whether a value has the required shape of an API error."""
    if not _is_mapping(value):
        return False
    return _has_string(value, "code") and _has_string(value, "message")


def is_api_meta(value: object) -> TypeGuard[ApiMeta]:
    """Return whether a value has valid optional request or pagination metadata."""
    if not _is_mapping(value):
        return False
    for field_name in ("request_id",):
        if field_name in value and not isinstance(value[field_name], str):
            return False
    for field_name in ("page", "page_size", "total"):
        if field_name in value and (not isinstance(value[field_name], int) or isinstance(value[field_name], bool)):
            return False
    return True


def is_todo_response(value: object) -> TypeGuard[TodoResponse]:
    """Return whether a value is a serialized Todo with valid nullable fields."""
    if not _is_mapping(value):
        return False
    return (
        _has_string(value, "id")
        and _has_string(value, "text")
        and isinstance(value.get("completed"), bool)
        and isinstance(value.get("created_at"), str)
        and _has_nullable_string(value, "completed_at")
        and isinstance(value.get("position"), int)
        and not isinstance(value.get("position"), bool)
    )


def is_note_response(value: object) -> TypeGuard[NoteResponse]:
    """Return whether a value is a serialized Note with required title/content fields."""
    if not _is_mapping(value):
        return False
    return all(_has_string(value, field_name) for field_name in ("id", "title", "content", "created_at", "updated_at"))


def is_pomodoro_session_response(value: object) -> TypeGuard[PomodoroSessionResponse]:
    """Return whether a value is a serialized Pomodoro session."""
    if not _is_mapping(value):
        return False
    duration = value.get("duration_seconds")
    return (
        _has_string(value, "id")
        and _has_nullable_string(value, "work_item_id")
        and _has_nullable_string(value, "started_at")
        and _has_nullable_string(value, "ended_at")
        and isinstance(duration, int)
        and not isinstance(duration, bool)
        and isinstance(value.get("completed"), bool)
    )


def is_work_item_response(value: object) -> TypeGuard[WorkItemResponse]:
    """Return whether a value is a serialized WorkItem with nullable ownership fields."""
    if not _is_mapping(value):
        return False
    return (
        all(_has_string(value, field_name) for field_name in ("id", "type", "title", "description", "status", "priority", "created_at", "updated_at"))
        and _has_nullable_string(value, "parent_id")
        and _has_nullable_string(value, "assigned_to")
    )


def is_comment_response(value: object) -> TypeGuard[CommentResponse]:
    """Return whether a value is a serialized WorkItem comment."""
    if not _is_mapping(value):
        return False
    return all(_has_string(value, field_name) for field_name in ("id", "work_item_id", "author", "content", "created_at", "updated_at"))


def is_api_payload(value: object) -> TypeGuard[ApiPayload]:
    """Return whether a value contains only valid optional DeskOS resource collections."""
    if not _is_mapping(value):
        return False
    collection_guards = {
        "todos": is_todo_response,
        "notes": is_note_response,
        "pomodoro_sessions": is_pomodoro_session_response,
        "work_items": is_work_item_response,
        "comments": is_comment_response,
    }
    for field_name, guard in collection_guards.items():
        collection = value.get(field_name)
        if collection is not None and (not isinstance(collection, list) or not all(guard(entry) for entry in collection)):
            return False
    return True


def is_api_response(value: object) -> TypeGuard[ApiResponse]:
    """Return whether a value is a safe-to-consume DeskOS API response envelope."""
    if not _is_mapping(value):
        return False
    data = value.get("data")
    error = value.get("error")
    meta = value.get("meta")
    return (
        (data is None or is_api_payload(data))
        and (error is None or is_api_error(error))
        and (meta is None or is_api_meta(meta))
    )
