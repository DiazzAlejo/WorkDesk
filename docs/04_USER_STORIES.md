# User Stories and Acceptance Criteria

## Dashboard

- As a user, I can see personal productivity and engineering work in one Dashboard.
- As a user, I can resize the window without losing access to the five board columns.

## Todos

- As a user, I can add, edit, complete, delete, and reorder a lightweight Todo.
- As a user, I can see completed Todos on the day they were completed.
- As a user, I do not see yesterday's completed Todo in the active Dashboard list, while its record remains in history.
- As a user, completing a Todo never creates or changes a WorkItem.

## Notes

- As a user, I can create a titled Note.
- As a user, I can click a Note title to open its editor.
- As a user, edits autosave after a debounce and show a Saved state.

## Pomodoro

- As a user, I can start, pause, resume, reset, and complete a 25-minute Pomodoro.
- As a user, I can select a custom duration.
- As a user, I can associate a session with a WorkItem or leave it unassociated.
- As a user, completed sessions remain in history with timestamps and duration.

## WorkItems

- As a user, I can create a Feature, User Story, or Task.
- As a user, I can create valid parent/child relationships and receive a clear validation error for invalid relationships.
- As a user, I can move a WorkItem between the five statuses without moving its children.
- As a user, I can filter by WorkItem type without destroying hierarchy context.
- As a user, I can expand and collapse parents inline.
- As a user, I can open a WorkItem detail view and manage its fields and comments.

## Comments

- As a user, I can add and edit a comment on a WorkItem.
- As a user, a comment cannot be attached to a different WorkItem by accident.
