# Decisions and Technical Debt

## Decisions

### Separate Todo and WorkItem

A Todo is intentionally a personal checklist record. A WorkItem participates in engineering hierarchy and workflow. No implicit conversion exists.

### JSON in Phase 1

Keep local JSON because it matches the requested local-first application and avoids uncontrolled migration. Hide it behind repositories and use a versioned schema so migration remains possible.

### Rotating Local Backups

Before replacing the primary JSON file, retain up to three previous generations as `.bak`, `.bak.1`, and `.bak.2`. This preserves recovery options without adding a separate backup subsystem in Phase 1.

### Parent Status Independence

Moving a parent changes only that WorkItem. Automatic cascading is excluded because it can cause surprising workflow changes and is not required by the first version.

### UI-First Contracts

Service contracts are specified before implementation so Dashboard interactions do not dictate persistence structure.

### Build-Review-Refactor-Test Loop

DeskOS uses small implementation slices followed by code reading, one focused refactor, and verification. This keeps AI-assisted changes reviewable and prevents structural debt from accumulating until a rewrite is required. The cadence is documented in `docs/11_REFACTORING_WORKFLOW.md`.

## Open Decisions to Resolve During Implementation

- Exact Python packaging and dependency strategy after baseline inspection.
- Whether the existing application uses `unittest` only or supports an additional UI test harness.
- Whether a single JSON document or separate versioned files performs better after real usage and failure testing.
- Exact priority values and default priority.
- Whether reopening a Todo clears `completed_at` or records a separate completion event.

## Technical Debt / Follow-Up

- Add a formal migration runner as the JSON schema evolves.
- Consider SQLite when query volume, history, or concurrent writes make JSON unwieldy.
- Add robust accessibility review for keyboard drag/drop alternatives.
- Add attachment storage only after the document use case is defined.
- Add settings grouping and backup/import/export workflows.
- Add performance tests for large WorkItem hierarchies.
