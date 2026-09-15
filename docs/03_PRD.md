# Product Requirements Document

## Product

DeskOS is a local desktop workspace for individual productivity and engineering work tracking.

## Problem

A quick personal Todo should remain lightweight, while engineering work needs hierarchy, explicit workflow status, filtering, and detail context. Combining both into one Task model creates confusing behavior and weakens future backend contracts.

## Goals

- Make the Dashboard the first and most useful screen.
- Keep personal productivity fast and low ceremony.
- Provide a structured Feature -> User Story -> Task work board.
- Preserve local-first JSON persistence behind service boundaries.
- Establish a backend-ready contract without premature cloud or multi-user features.

## Non-Goals: Phase 1

Cloud synchronization, authentication, roles, permissions, AI, collaboration, complex attachments, automatic parent/child status propagation, and migration to a database.

## Functional Requirements

### Dashboard

The Dashboard has a header, a personal workspace, and a visually dominant five-column engineering board. It resizes using Tkinter geometry managers and supports horizontal board scrolling when needed.

### Personal Workspace

- Pomodoro defaults to 25 minutes and supports start, pause, resume, reset, custom duration, completion, history, and optional WorkItem association.
- Todos support create, edit, delete, complete, and reorder. Completed records remain stored and are visible on their completion day only.
- Notes require titles, show titles in the Dashboard list, open in a modal editor, autosave with debounce, and show a Saved indicator.

### Engineering Board

- Columns are New, Active, On Hold, Resolved, and Closed.
- WorkItems can be dragged between columns; moving updates status through `WorkItemService`.
- Type, title, description/status context, and useful hierarchy indicators appear on cards.
- Parents expand inline to reveal children. Filtering by All, Feature, User Story, or Task preserves hierarchy relationships.
- Clicking a card opens a detail view with editable title, description, type, status, priority, parent, assignee, comments, and a future-ready document section.

## Quality Requirements

The UI must remain keyboard-friendly, resize safely, avoid absolute positioning, keep persistence out of widgets, and maintain focused tests for service invariants and user-visible behavior.

## Success Criteria

A user can open DeskOS, create a personal Todo without creating a WorkItem, create a valid Feature/User Story/Task hierarchy, move a WorkItem between statuses, expand/filter the board, complete a Pomodoro linked to a WorkItem, and edit a Note with debounced persistence.
