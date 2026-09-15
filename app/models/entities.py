from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


def datetime_to_json(timestamp: Optional[datetime]) -> Optional[str]:
    return timestamp.isoformat() if timestamp else None


def datetime_from_json(serialized_timestamp: Optional[str]) -> Optional[datetime]:
    if not serialized_timestamp:
        return None
    parsed = datetime.fromisoformat(serialized_timestamp)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


class WorkItemType(str, Enum):
    FEATURE = "FEATURE"
    USER_STORY = "USER_STORY"
    TASK = "TASK"


class WorkItemStatus(str, Enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Todo:
    text: str
    id: str = field(default_factory=new_id)
    completed: bool = False
    created_at: datetime = field(default_factory=utc_now)
    completed_at: Optional[datetime] = None
    position: int = 0

    def __post_init__(self) -> None:
        self.text = self.text.strip()
        if not self.text:
            raise ValueError("Todo text is required")

    def to_dict(self) -> Dict[str, Any]:
        serialized_todo = asdict(self)
        serialized_todo["created_at"] = datetime_to_json(self.created_at)
        serialized_todo["completed_at"] = datetime_to_json(self.completed_at)
        return serialized_todo

    @classmethod
    def from_dict(cls, serialized_todo: Dict[str, Any]) -> "Todo":
        return cls(
            id=serialized_todo["id"], text=serialized_todo["text"], completed=serialized_todo.get("completed", False),
            created_at=datetime_from_json(serialized_todo["created_at"]) or utc_now(),
            completed_at=datetime_from_json(serialized_todo.get("completed_at")), position=serialized_todo.get("position", 0),
        )


@dataclass
class Note:
    title: str
    content: str = ""
    id: str = field(default_factory=new_id)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Note title is required")

    def to_dict(self) -> Dict[str, Any]:
        serialized_note = asdict(self)
        serialized_note["created_at"] = datetime_to_json(self.created_at)
        serialized_note["updated_at"] = datetime_to_json(self.updated_at)
        return serialized_note

    @classmethod
    def from_dict(cls, serialized_note: Dict[str, Any]) -> "Note":
        return cls(
            id=serialized_note["id"], title=serialized_note["title"], content=serialized_note.get("content", ""),
            created_at=datetime_from_json(serialized_note["created_at"]) or utc_now(),
            updated_at=datetime_from_json(serialized_note["updated_at"]) or utc_now(),
        )


@dataclass
class PomodoroSession:
    duration_seconds: int = 1500
    work_item_id: Optional[str] = None
    id: str = field(default_factory=new_id)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["started_at"] = datetime_to_json(self.started_at)
        result["ended_at"] = datetime_to_json(self.ended_at)
        return result

    @classmethod
    def from_dict(cls, serialized_session: Dict[str, Any]) -> "PomodoroSession":
        return cls(
            id=serialized_session["id"], duration_seconds=serialized_session["duration_seconds"], work_item_id=serialized_session.get("work_item_id"),
            started_at=datetime_from_json(serialized_session.get("started_at")), ended_at=datetime_from_json(serialized_session.get("ended_at")),
            completed=serialized_session.get("completed", False),
        )


@dataclass
class WorkItem:
    type: WorkItemType
    title: str
    description: str = ""
    status: WorkItemStatus = WorkItemStatus.NEW
    priority: Priority = Priority.MEDIUM
    parent_id: Optional[str] = None
    assigned_to: Optional[str] = None
    id: str = field(default_factory=new_id)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    tags: list[str] = field(default_factory=list)
    due_date: Optional[date] = None
    estimate: Optional[float] = None
    created_by: Optional[str] = None

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Work item title is required")
        self.type = WorkItemType(self.type)
        self.status = WorkItemStatus(self.status)
        self.priority = Priority(self.priority)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["type"] = self.type.value
        result["status"] = self.status.value
        result["priority"] = self.priority.value
        result["created_at"] = datetime_to_json(self.created_at)
        result["updated_at"] = datetime_to_json(self.updated_at)
        result["due_date"] = self.due_date.isoformat() if self.due_date else None
        return result

    @classmethod
    def from_dict(cls, serialized_work_item: Dict[str, Any]) -> "WorkItem":
        due_date = date.fromisoformat(serialized_work_item["due_date"]) if serialized_work_item.get("due_date") else None
        return cls(
            id=serialized_work_item["id"], type=WorkItemType(serialized_work_item["type"]), title=serialized_work_item["title"], description=serialized_work_item.get("description", ""),
            status=WorkItemStatus(serialized_work_item.get("status", WorkItemStatus.NEW.value)), priority=Priority(serialized_work_item.get("priority", Priority.MEDIUM.value)),
            parent_id=serialized_work_item.get("parent_id"), assigned_to=serialized_work_item.get("assigned_to"),
            created_at=datetime_from_json(serialized_work_item["created_at"]) or utc_now(), updated_at=datetime_from_json(serialized_work_item["updated_at"]) or utc_now(),
            tags=serialized_work_item.get("tags", []), due_date=due_date, estimate=serialized_work_item.get("estimate"), created_by=serialized_work_item.get("created_by"),
        )


@dataclass
class Comment:
    work_item_id: str
    author: str
    content: str
    id: str = field(default_factory=new_id)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.content = self.content.strip()
        if not self.content:
            raise ValueError("Comment content is required")
        if not self.author.strip():
            raise ValueError("Comment author is required")

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["created_at"] = datetime_to_json(self.created_at)
        result["updated_at"] = datetime_to_json(self.updated_at)
        return result

    @classmethod
    def from_dict(cls, serialized_comment: Dict[str, Any]) -> "Comment":
        return cls(
            id=serialized_comment["id"], work_item_id=serialized_comment["work_item_id"], author=serialized_comment["author"], content=serialized_comment["content"],
            created_at=datetime_from_json(serialized_comment["created_at"]) or utc_now(), updated_at=datetime_from_json(serialized_comment["updated_at"]) or utc_now(),
        )
