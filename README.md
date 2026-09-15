# DeskOS

DeskOS is a local Tkinter desktop application combining personal productivity with structured engineering work management.

## Current Repository State

The repository contains the Phase 1 Tkinter implementation described by the documentation and its focused test suite.

## Product Shape

Personal productivity:

- Dashboard-only Todos
- Notes with debounced autosave
- Pomodoro sessions, optionally associated with a WorkItem

Engineering work management:

- Features contain User Stories
- User Stories contain Tasks
- WorkItems move through `NEW`, `ACTIVE`, `ON_HOLD`, `RESOLVED`, and `CLOSED`

## Documentation Map

- `AGENTS.md`: engineering rules for future agents and contributors
- `docs/01_ANALYSIS.md`: repository baseline and inspection record
- `docs/02_DATA_MODEL.md`: domain entities and relationships
- `docs/03_PRD.md`: product requirements and scope
- `docs/04_USER_STORIES.md`: user stories and acceptance criteria
- `docs/05_SERVICE_CONTRACTS.md`: service interfaces and invariants
- `docs/06_ARCHITECTURE.md`: application boundaries and data flow
- `docs/06_IMPLEMENTATION_PLAN.md`: vertical implementation slices
- `docs/07_UI_UX_SPECIFICATION.md`: Dashboard interaction and visual specification
- `docs/08_BACKEND_CONTRACT.md`: next-phase API/backend contract
- `docs/09_DECISIONS.md`: decisions, assumptions, and technical debt
- `docs/10_TEST_PLAN.md`: verification strategy
- `docs/11_REFACTORING_WORKFLOW.md`: Build → Review → Refactor → Test workflow and schedule

Review the documentation before changing behavior, then run focused tests and `python -m pytest -q` before release.

## Run

```text
python run.py
python -m unittest discover -s tests -v
```

The application stores local data in `data/deskos.json`, which is ignored by Git. Before each replacement, the repository rotates up to three backups: `.bak`, `.bak.1`, and `.bak.2`. The current implementation uses only the Python standard library and Tkinter.

UI workflow tests use the shared Tkinter harness in `tests/ui_harness.py`; it creates a withdrawn root, pumps events, and destroys the root after each test.

## Windows Desktop Release

Download the latest Windows ZIP from the GitHub Releases page, extract it, and double-click `WorkDesk.exe`. No Python installation is required. The packaged app stores its local data in `%LOCALAPPDATA%\WorkDesk`.

To build the release artifact on Windows:

```powershell
python -m pip install pyinstaller
.\build_windows.ps1
```

The script creates `dist\WorkDesk-windows-x64.zip`.
