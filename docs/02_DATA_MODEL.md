# Data Model

## Principles

- Personal and engineering concepts are separate.
- IDs are stable opaque strings or UUIDs.
- Timestamps are timezone-aware UTC values at the service boundary and serialized consistently by storage.
- Nullable relationships are explicit.
- Enum-like values are defined centrally, not arbitrary UI strings.

## Todo

| Field | Type | Rules |
|---|---|---|
| `id` | ID | Required, stable |
| `text` | string | Required, non-empty after trimming |
| `completed` | boolean | Defaults to `false` |
| `created_at` | datetime | Required |
| `completed_at` | datetime or null | Set on first completion; cleared if reopened only if product policy permits |
| `position` | integer | Ordering among Dashboard Todos |

Completed Todos remain persisted. The Dashboard hides completed records after their completion calendar day.

## Note

`id`, `title`, `content`, `created_at`, and `updated_at` are required. `title` must be non-empty. Notes are not WorkItems.

## PomodoroSession

`id`, nullable `work_item_id`, `started_at`, `ended_at`, `duration_seconds`, and `completed` are required. A paused session is represented by service state during an active session; completed history stores the final timestamps and duration.

## WorkItem

| Field | Type | Rules |
|---|---|---|
| `id` | ID | Required |
| `type` | `WorkItemType` | `FEATURE`, `USER_STORY`, or `TASK` |
| `title` | string | Required |
| `description` | string | Optional |
| `status` | `WorkItemStatus` | `NEW`, `ACTIVE`, `ON_HOLD`, `RESOLVED`, `CLOSED` |
| `priority` | `Priority` | Defined value set; default documented by implementation |
| `parent_id` | ID or null | Must satisfy hierarchy rules |
| `created_at` | datetime | Required |
| `updated_at` | datetime | Required |
| `assigned_to` | string or null | Optional |
| `tags` | list of strings | Future-ready |
| `due_date` | date or null | Future-ready |
| `estimate` | number or null | Future-ready |
| `created_by` | string or null | Future-ready |

Hierarchy constraints:

- Feature may be a root or have no parent in Phase 1.
- User Story may have a Feature parent.
- Task must have a User Story parent when hierarchical creation is used.
- Task cannot have children.
- Cycles are invalid.
- A child can become `ACTIVE` only when its parent is `ACTIVE`.
- Moving a parent to `ACTIVE` activates all of its descendants.
- A parent can become `RESOLVED` or `CLOSED` only when its direct children are `RESOLVED` or `CLOSED`.
- Closing a parent locks child changes until the parent is reopened.
- Completing all children rolls the parent up to `RESOLVED`; statuses otherwise remain independent.

## Comment

`id`, `work_item_id`, `author`, `content`, `created_at`, and `updated_at`. Comments belong to WorkItems and are not Notes.

## Document Placeholder

The WorkItem detail contract reserves a document collection boundary without requiring binary storage in Phase 1. Future attachment metadata should include an ID, WorkItem ID, filename, media type, size, storage reference, and timestamps.

## JSON Shape

Use a versioned root object rather than unrelated files embedded in UI code:

```json
{
  "schema_version": 1,
  "todos": [],
  "notes": [],
  "pomodoro_sessions": [],
  "work_items": [],
  "comments": [],
  "documents": []
}
```

Repository code owns migration, validation, atomic writes, and backup behavior.
