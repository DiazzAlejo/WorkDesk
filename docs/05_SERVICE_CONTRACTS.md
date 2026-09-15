# Service Contracts

Services are the UI-facing application boundary. Concrete implementations may use JSON repositories in Phase 1 and a database repository later.

## TodoService

```text
create(text) -> Todo
get(todo_id) -> Todo | NotFound
list(include_completed_history, today) -> list[Todo]
update(todo_id, text) -> Todo
complete(todo_id, completed_at) -> Todo
reopen(todo_id) -> Todo
delete(todo_id) -> None
reorder(todo_ids) -> list[Todo]
```

Rules: reject empty text, preserve completion history, and make reorder atomic with respect to the submitted set.

## NoteService

```text
create(title, content="") -> Note
get(note_id) -> Note | NotFound
list() -> list[Note]
update(note_id, title, content) -> Note
delete(note_id) -> None
```

`update` changes `updated_at`. The UI owns debounce timing; the service owns persistence and validation.

## PomodoroService

```text
start(duration_seconds=1500, work_item_id=None, started_at=None) -> ActivePomodoro
pause(session_id, paused_at=None) -> ActivePomodoro
resume(session_id, resumed_at=None) -> ActivePomodoro
reset(session_id) -> None
complete(session_id, ended_at=None) -> PomodoroSession
list_history() -> list[PomodoroSession]
```

Default duration is 1500 seconds. WorkItem association is nullable and must reference an existing WorkItem when present.

## WorkItemService

```text
create(type, title, description, status, priority, parent_id=None, assigned_to=None) -> WorkItem
get(work_item_id) -> WorkItem | NotFound
list(filters=None) -> list[WorkItem]
update(work_item_id, patch) -> WorkItem
delete(work_item_id) -> None
move(work_item_id, status) -> WorkItem
get_children(parent_id) -> list[WorkItem]
get_hierarchy(filters=None) -> WorkItemTree
```

Creation and parent changes validate hierarchy type rules and cycles. `move` changes only the selected WorkItem.

## CommentService

```text
create(work_item_id, author, content) -> Comment
get(comment_id) -> Comment | NotFound
list_for_work_item(work_item_id) -> list[Comment]
update(comment_id, content) -> Comment
delete(comment_id) -> None
```

Comments require an existing WorkItem and non-empty content.

## Repository Boundary

Repositories provide persistence operations to services. They must not expose file paths, Tkinter objects, or JSON implementation details to UI code. Repository errors are translated by services into stable domain/application errors.
