# Test Plan

## Test Layers

- Model tests: validation, enum constraints, datetime behavior, serialization.
- Repository tests: persistence, atomicity, malformed input, schema versioning.
- Service tests: domain rules and timestamps using injectable clocks.
- UI tests: only where the Tkinter test setup can reliably exercise behavior; keep most rules in services.
- Smoke/integration tests: application startup and representative Dashboard workflows.

## Todo Coverage

Test create, edit, delete, complete, completion timestamp, same-day visibility, next-day hiding, preservation in history, reopening policy, and reorder persistence.

## Note Coverage

Test required title, create, update content, updated timestamp, list display data, and debounced autosave resulting in one service update after the debounce window. Test flush-on-close behavior.

## Pomodoro Coverage

Test 25-minute default, custom duration, start, pause, resume, reset, completion, completed timestamps, history persistence, and nullable/valid WorkItem association.

## WorkItem Coverage

Test Feature, User Story, and Task creation; valid parent relationships; invalid parent types; task child rejection; cycle rejection; status changes; independent parent/child moves; children retrieval; hierarchy output; and type/status/priority filtering.

## Comment Coverage

Test create, required content, WorkItem association, list by WorkItem, update timestamp, and deletion.

## UI Acceptance Checks

- Dashboard opens with empty/loading/error states.
- Window resizing preserves usable controls.
- Board scrolls horizontally at narrow widths.
- Drag/drop and keyboard move both update through the service.
- Parent expansion and filtering preserve understandable hierarchy.
- Note editor shows saving/saved/error states.
- Timer controls reflect service state and do not lose history.

## Tkinter Workflow Harness

`tests/ui_harness.py` owns a hidden root, temporary JSON path, event pumping, and deterministic teardown. Workflow tests should use it for service-backed UI behavior and should avoid relying on window-manager focus when running headlessly.

## Execution Order

Run focused tests for the current slice first, then the complete suite before merging. Never remove existing tests to make a slice pass.
