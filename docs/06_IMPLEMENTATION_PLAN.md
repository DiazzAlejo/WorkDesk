# Implementation Plan

Implement in small vertical slices. Each slice follows the repository loop in `docs/11_REFACTORING_WORKFLOW.md`:

```text
Build -> Review -> Refactor -> Test -> Repeat
```

Each slice should leave the application runnable, receive a short code review, and include focused tests before starting the next slice.

## Slice 0: Baseline and Scaffold (Complete)

Confirm Python version, test command, packaging, and current repository state. Create the target package/test layout only as needed. Add a smoke test for application startup.

Exit criteria: documented runtime commands and a passing baseline test.

## Slice 1: Shared Domain Primitives (Complete)

Add IDs, UTC datetime handling, enums, validation errors, and model serialization boundaries.

Exit criteria: model tests cover required fields, enum values, and round-trip serialization.

## Slice 2: Versioned JSON Repository (Complete)

Implement repository protocols, versioned root document, atomic writes, load validation, and backup/error behavior.

Exit criteria: repository tests cover empty state, persistence, malformed data, and schema version handling.

## Slice 3: Services and Personal Productivity (Complete)

Implement TodoService, NoteService, and PomodoroService with focused tests. Keep UI absent or minimal until contracts are stable.

Exit criteria: all Todo, Note, and Pomodoro requirements in `docs/10_TEST_PLAN.md` pass.

## Slice 4: Dashboard Shell (Complete)

Build the header, personal workspace region, board region, resizing rules, styles, and placeholder states. Wire dependency injection for services.

Exit criteria: Dashboard opens, resizes, and displays service-backed empty states.

## Slice 5: Personal Workspace UI (Implemented, needs display-driven QA)

Implement Pomodoro controls/history, Todo checklist/reorder, and Note list/editor/autosave. Add UI tests only where the existing test architecture can support them reliably.

Exit criteria: personal workflows are usable without direct persistence access from widgets.

## Slice 6: WorkItem Domain and Service (Complete)

Implement hierarchy validation, filtering, children retrieval, move semantics, and WorkItem persistence.

Exit criteria: invalid hierarchy and independent parent/child status behavior are tested.

## Slice 7: Work Board (Implemented, needs display-driven QA)

Implement five columns, cards, expansion, filtering, drag/drop, keyboard move action, and refresh/error states.

Exit criteria: board interactions call WorkItemService and all board service tests pass.

## Slice 8: Details and Comments (Implemented, needs display-driven QA)

Implement WorkItem detail panel/modal, edit fields, comments, and document placeholder boundary.

Exit criteria: detail edits and comment association/update tests pass.

## Slice 9: Integration and Regression

Run the full suite, exercise startup and representative workflows, inspect persistence output, and fix only regressions caused by the feature.

Exit criteria: full test suite passes and no UI path writes storage directly.

## Slice 10: Documentation Closeout

Update README, requirements, architecture, data model, user stories, and decisions to reflect verified implementation details. Record technical debt and backend follow-up work.

Exit criteria: the refactoring workflow and final validation results are documented.
