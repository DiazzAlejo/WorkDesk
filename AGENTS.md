# DeskOS Agent Instructions

## Scope

These instructions apply to all work in this repository. DeskOS is a Python 3.8+ Tkinter desktop application for personal productivity and engineering work management.

## Product Boundaries

- Keep personal productivity separate from engineering work management.
- `Todo`, `Note`, and `PomodoroSession` are personal productivity models.
- `WorkItem` is the engineering model with the hierarchy `Feature > User Story > Task`.
- A Todo must never be promoted to or silently converted into a WorkItem.
- Do not add cloud sync, authentication, AI, or multi-user collaboration in Phase 1.

## Architecture Rules

- Preserve the separation between models, services, storage, UI, and tests.
- UI code communicates with services, never directly with JSON files.
- Keep JSON persistence behind repository/service abstractions so SQLite or another store can be introduced later.
- Reuse existing functionality after inspection; do not rewrite working behavior without recording the reason in `docs/09_DECISIONS.md`.
- Prefer small, testable service methods and typed value sets/enums over free-form strings for statuses and item types.
- Avoid new dependencies unless the standard library and existing project patterns cannot satisfy the requirement.

## Dashboard Rules

- The Dashboard is the primary user experience and has a personal workspace plus a visually dominant engineering work board.
- The work board has exactly these statuses: `NEW`, `ACTIVE`, `ON_HOLD`, `RESOLVED`, and `CLOSED`.
- Moving a parent to `ACTIVE` activates its descendants; resolving or closing requires completed children and resolution rolls up.
- WorkItem filtering must preserve hierarchy relationships.
- Notes autosave through a debounced service call and expose a subtle saved state.
- Completed Todos remain stored for history and are hidden from the active list after the completion day.

## Implementation Workflow

1. Inspect the repository and record verified facts before changing existing code.
2. Update the relevant specification when behavior or contracts change.
3. Implement one small vertical slice at a time from `docs/06_IMPLEMENTATION_PLAN.md`.
4. Review the generated code before continuing: check duplication, file/function size, naming, boundaries, and missing tests.
5. Refactor one pressing issue at a time using `utils/`, `hooks/`, `types/`, or feature-local ownership as appropriate.
6. Add or update focused unit tests with every service/model/refactor change.
7. Run the focused test, then the full test suite when the slice is complete.
8. Keep unrelated changes out of the slice.

Use the repeatable loop documented in `docs/11_REFACTORING_WORKFLOW.md`:

```text
Build -> Review -> Refactor -> Test -> Repeat
```

Follow its schedule: review every session, perform a duplication/naming review weekly, audit structure monthly, and run a full validation pass before launch.

## Documentation Sources of Truth

- Product scope: `docs/03_PRD.md`
- Data model: `docs/02_DATA_MODEL.md`
- Architecture: `docs/06_ARCHITECTURE.md`
- UI behavior: `docs/07_UI_UX_SPECIFICATION.md`
- Delivery order: `docs/06_IMPLEMENTATION_PLAN.md`
- Backend/API contract: `docs/08_BACKEND_CONTRACT.md`
- Decisions and tradeoffs: `docs/09_DECISIONS.md`
- Refactoring workflow: `docs/11_REFACTORING_WORKFLOW.md`

## Definition of Done

A change is complete only when its behavior, service boundary, persistence implications, tests, and documentation are aligned. Do not claim existing functionality was preserved until the relevant code and tests have actually been inspected.
