# UI/UX Specification

## Dashboard Composition

The main window contains a header and a two-region body. The left Personal Workspace is compact; the right Engineering Work Board receives the dominant width. Use `grid`, `pack`, minimum sizes, scrollable frames, and horizontal scrolling rather than absolute coordinates.

## Personal Workspace

### Pomodoro

Show a prominent `FOCUS` label, timer, optional WorkItem selector, and Start/Pause/Resume/Reset actions. Default display is `25:00`. The selected WorkItem title is visible. Timer transitions are driven by a service/controller state, not by widget-local persistence.

### Todo

Use a lightweight checklist presentation with an add control, inline or modal editing, completion affordance, delete action, and reorder interaction. Active Todos appear first. Same-day completed Todos remain visible below active items; older completed records are excluded from the active Dashboard view.

### Notes

Show titled rows. Clicking a row opens a sticky-note-style modal. The editor has title and content fields, a close action, and a subtle `Saved`/saving state. Autosave is debounced and flushes pending changes when the editor closes.

## Engineering Work Board

Show a filter control above five horizontally arranged columns: New, Active, On Hold, Resolved, Closed. Cards are compact but readable and display type, title, relevant description/status context, and hierarchy indicators. Cards support keyboard focus and an accessible move action in addition to drag/drop.

Parent expansion controls appear on cards with children in the `All Work Items` view. Type filters show only the selected Feature, User Story, or Task cards and hide expansion controls. Parent status changes follow the hierarchy rules in the data model.

## WorkItem Detail

Open a modal or side panel from a card. Include editable title, description, type, status, priority, parent, assignee, comments, and a document placeholder. Save operations go through services and show validation errors near the affected field.

## Visual Language

Use consistent typography, restrained borders, compact spacing, clear active/hover/focus states, and distinct but not excessive visual indicators for Feature, User Story, and Task. Avoid relying on color alone for status or type.

## Responsive Behavior

At narrow widths, the Personal Workspace may stack above the board while the board remains horizontally scrollable. The window must not depend on fixed absolute positions. Dialog content should grow with the window and remain keyboard navigable.

## Interaction States

Specify loading, empty, validation-error, persistence-error, disabled, hover, keyboard-focus, dragging, saving, and saved states before implementation. Every destructive action requires confirmation where accidental loss is plausible.
