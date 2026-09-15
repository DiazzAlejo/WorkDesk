# Architecture

## Layers

```text
Tkinter UI
  -> application services
    -> repositories
      -> versioned JSON storage
```

Models and value sets are shared by the relevant layers but contain no Tkinter or file I/O code.

## Suggested Layout

```text
app/
  main.py
  window.py
  styles.py
  models/
    todo.py
    note.py
    pomodoro.py
    work_item.py
    comment.py
    enums.py
  services/
    todo_service.py
    note_service.py
    pomodoro_service.py
    work_item_service.py
    comment_service.py
  storage/
    repository.py
    json_repository.py
    migrations.py
  ui/
    features/
      dashboard/
        dashboard_view.py
      todos/
        todo_panel.py
        todo_row.py
      notes/
        notes_panel.py
        note_row.py
        note_editor.py
      pomodoro/
        pomodoro_panel.py
      work_items/
        work_board.py
        work_item_card.py
        status_column.py
        status_config.py
        work_item_tree.py
        work_item_dialog.py
        work_item_detail.py
    shared/
      components/
        dashboard_header.py
        section_frame.py
      theme/
        theme.py
    types/
      callbacks.py
      state.py
      types.py
    utils/
      tkinter_helpers.py
      formatting.py
      lists.py
      forms.py
      debounce.py
    shared/dialogs/
      service_dialog.py
    hooks/
      dashboard_hook.py
      pomodoro_hook.py
      debounce_hook.py
tests/
  ui_harness.py
docs/
```

This is a target structure, not a claim about existing files.

## Data Flow Examples

A board drop calls `WorkItemService.move`, refreshes the affected card/column, and reports a service error without touching JSON from the widget. A Note edit schedules a debounced callback, which calls `NoteService.update`; the editor updates its Saved state from the result.

## Storage

Phase 1 uses a versioned JSON document with atomic temp-file replacement and a backup/error strategy. The JSON adapter should be replaceable behind repository protocols. Do not let the Dashboard know the storage path.

## Error Handling

Services expose domain errors such as validation failure, not found, invalid hierarchy, conflict, and persistence failure. UI dialogs render user-facing messages; models remain UI-agnostic.

## Settings

Keep Settings separate from Dashboard implementation. Reserve future groupings for Personal, WorkDesk, and Admin without implementing users/roles/permissions in Phase 1.
