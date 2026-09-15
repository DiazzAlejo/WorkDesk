# Refactoring Workflow

Prompts are tools, but tools need a repeatable system. DeskOS follows this loop:

```text
Build -> Review -> Refactor -> Test -> Repeat
```

## Build: Stop Sooner

Implement small vertical slices instead of requesting a complete feature in one pass. A slice should have one clear behavior and a narrow validation check. Pause after the slice so the code can be read before adding the next piece.

## Review: Read the Output

After each implementation session, spend a short focused interval reading the changed code. Look for:

- Obvious duplication
- Files or functions that are too long
- Names that do not express domain intent
- UI code reaching into persistence
- Business rules hidden inside widgets
- Missing focused tests

This is a code-reading step, not a debugging session. Record meaningful findings before changing them.

## Refactor: One Concern at a Time

Choose the most pressing issue and refactor only that concern. Prefer the smallest extraction that improves ownership or testability:

- Move pure logic into `utils/`.
- Move reusable stateful coordination into `hooks/`.
- Move shared contracts and value shapes into `types/`.
- Group feature-specific UI with its feature.
- Preserve service and repository boundaries.

Do not combine unrelated naming, structure, UI, and behavior changes in one refactor slice.

## Test: Prove the Slice

After each refactor:

1. Run the narrowest relevant test.
2. Run compilation or diagnostics.
3. Run the full test suite when the slice is complete.
4. Perform manual UI checks when the change affects Tkinter layout or interaction.

A refactor is complete only when behavior is preserved and the new ownership boundary has focused coverage.

## Schedule

| Frequency | Practice |
|---|---|
| Every session | Read changed code for a short review before stopping. |
| Weekly | Review new code for duplication, naming, and misplaced responsibilities. |
| Monthly | Audit feature structure, shared utilities, hooks, and types. |
| Before launch | Run the full test suite, startup smoke test, naming/type review, and manual UI workflow checks. |

Refactoring is part of normal delivery, not a one-time rewrite event.

## Related Guidance

- [Implementation plan](06_IMPLEMENTATION_PLAN.md)
- [Test plan](10_TEST_PLAN.md)
- [Architecture](06_ARCHITECTURE.md)
