# Backend Contract

This contract is the next-phase integration target. Phase 1 may implement it as in-process Python services over JSON repositories.

## Resource Operations

All resources support create, get, list, update, and delete where applicable. Responses return domain objects with stable IDs and timestamps. Validation failures are structured and identify the field or relationship that failed.

## WorkItem Operations

```text
POST   /work-items
GET    /work-items/{id}
GET    /work-items?type=&status=&priority=&assigned_to=&tag=
PATCH  /work-items/{id}
DELETE /work-items/{id}
POST   /work-items/{id}/move
GET    /work-items/{id}/children
GET    /work-items/hierarchy
```

`move` accepts one defined status. Hierarchy responses include parent/child relationships without changing stored statuses.

## Personal Operations

```text
GET/POST/PATCH/DELETE /todos
POST /todos/{id}/complete
POST /todos/reorder
GET/POST/PATCH/DELETE /notes
POST /pomodoro-sessions/start
POST /pomodoro-sessions/{id}/pause
POST /pomodoro-sessions/{id}/resume
POST /pomodoro-sessions/{id}/complete
GET  /pomodoro-sessions
```

## Comments and Documents

```text
GET/POST /work-items/{id}/comments
PATCH/DELETE /comments/{id}
GET /work-items/{id}/documents
```

Document upload/storage is intentionally deferred. The response shape should reserve metadata without forcing binary transport now.

## Error Contract

Use stable categories: `not_found`, `validation_error`, `invalid_hierarchy`, `conflict`, and `persistence_error`. The desktop UI can map these categories to dialogs, inline errors, or retry actions.

## Future Compatibility

The contract must not assume JSON file paths, Tkinter event objects, or a single process. Date/time values use an explicit ISO 8601 representation, and enum values are stable uppercase identifiers.
