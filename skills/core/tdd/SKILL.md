---
name: tdd
description: Build or fix behavior through a test-first red-green-refactor loop using small vertical slices and tests through public interfaces. Use when the target behavior is already understood and the user wants disciplined implementation or regression-test-driven bug fixing.
---

# Test-Driven Development

Use this skill for focused implementation work through a test-first loop.

## When to Use

Use this skill when the user wants to:

- implement a feature through TDD
- fix a bug through a regression test first
- work in a red-green-refactor loop
- break implementation into small vertical slices
- improve confidence by driving behavior through tests

## When Not to Use

Do not use this skill when:

- the main task is broad investigation, triage, or root-cause analysis; use `repository-technical-analysis`
- the main task is debugging a concrete failing behavior that still needs repro and isolation; use `diagnose`
- the user only wants high-level planning with no implementation loop
- a repository-specific overlay already fully defines the implementation workflow

## Inputs

Accept any of:

- a target behavior to implement
- a bug fix with expected behavior
- a failing repro ready to convert into a regression test
- a user story, task, or issue with clear acceptance behavior
- local notes or artifacts describing the intended change

## First Read

- Read `AGENTS.md`, `README.md`, `Makefile`, and repo-specific contributor docs when present.
- If a local artifact exists for the task (prefer `$ARTIFACTS/<meaningful_id>/` paths per repo `ARTIFACTS.md`; legacy root-level files remain valid), read it first.
- Reuse repository-specific contributor skills for local commands and validation.
- Reuse `repository-technical-analysis` or `diagnose` first when the behavior or failure mode is still unclear.

## Workflow

1. Confirm the target behavior to build or fix.
2. Identify the narrowest public interface that can express that behavior.
3. Choose one small vertical slice.
4. Write one test for one observable behavior.
5. Run the test and confirm it fails for the right reason.
6. Write the smallest amount of code needed to make that test pass.
7. Re-run the test and confirm green.
8. Repeat for the next behavior slice.
9. After the necessary slices are green, refactor carefully while keeping tests green.
10. Run the smallest relevant validation set for the repo.

## Implementation Rules

- Prefer behavior through public interfaces over implementation detail testing.
- Prefer vertical slices over horizontal slicing.
- Write one test at a time.
- Add only the code needed for the current test.
- Do not speculate too far ahead.
- Refactor only after reaching green.
- Use regression tests when fixing bugs, but only after the target behavior is clear enough to encode.

## Anti-Patterns

Avoid:

- writing all tests first, then all implementation
- testing private methods or internal collaborators by default
- coupling tests tightly to implementation structure
- adding future-facing code before a test demands it
- refactoring while still red

## Validation

- Confirm each new test fails before the fix and passes after it.
- Prefer the smallest relevant test set while iterating.
- After approved changes, run the repo-appropriate validation commands from companion skills or local docs.
- When fixing a bug, re-run the original repro if one exists.

## Outputs / Artifacts

Return:

1. the behavior or slice being implemented
2. the test added or updated
3. the code change made to satisfy it
4. the validation run
5. any remaining gaps, blockers, or follow-up slices

When the work is non-trivial, this skill may also write:

- `$ARTIFACTS/<meaningful_id>/analysis_<relevant_name>.md` for new artifacts (see repo `ARTIFACTS.md`; extend existing paths in place)

## Companion Skills

Use this skill as a generic implementation-discipline layer.

Common pairings:

- `diagnose` to isolate a bug before driving the fix through tests
- `repository-technical-analysis` when broader investigation is still needed
- repository-specific contributor skills for local commands, validation, and conventions
- `python-fastapi-contributor` for Python or FastAPI implementation work

## Safety Notes

- Do not force TDD when the intended behavior is still ambiguous.
- Do not treat shallow implementation-detail tests as a substitute for behavior checks.
- Keep the loop small enough that each red-green step gives useful feedback.
