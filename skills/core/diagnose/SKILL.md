---
name: diagnose
description: Diagnose concrete bugs and regressions with a tight repro, hypothesis, and instrumentation loop. Use when a specific failing behavior already exists and the user wants disciplined debugging of a broken behavior, flaky issue, or performance regression.
---

# Diagnose

Use this skill for focused debugging work.

## When to Use

Use this skill when the user wants to:

- diagnose a concrete bug
- debug a flaky or non-deterministic issue
- investigate a performance regression
- build a reliable repro before fixing a bug
- run a disciplined hypothesis-and-instrumentation loop

## When Not to Use

Do not use this skill when:

- the task is broad repository investigation without a concrete failure mode; use `repository-technical-analysis`
- the main task is scoping, triage, or evidence collection before debugging begins; use `repository-technical-analysis`
- there is no concrete failing behavior, repro target, or regression signal yet
- the task is broad architecture review or multi-hypothesis repository exploration without a specific bug target
- the task is primarily remote transport access such as Jira or GitLab fetch
- the user only wants implementation with no meaningful debugging workflow
- a repository-specific overlay already fully defines the debugging workflow

## Inputs

Accept any of:

- a bug report
- failing test or command
- error message
- flaky behavior description
- performance regression description
- local artifact or notes describing prior investigation

## First Read

- Read `AGENTS.md`, `README.md`, `Makefile`, and any repo-specific contributor docs first when present.
- When the repro loop benefits from `entr`, `watchexec`, or `hyperfine`, check `command -v` first; if missing, **ask the user** to install with the command appropriate for their OS (`brew`, `apt`, `dnf`, …) before improvising (see **AGENTS.md** missing CLI tools).
- If the user provides a local artifact such as `$ARTIFACTS/<meaningful_id>/analysis_<name>.md` (or legacy root-level `analysis_<name>.md`), read it first.
- Reuse `repository-technical-analysis` expectations for evidence, confidence labels, and blockers.
- Do not edit code until the repro and failure mode are clear enough to defend.

## Workflow

1. Define the exact failure mode.
2. Build the narrowest reliable feedback loop you can:
   - failing test
   - targeted command
   - HTTP or script repro
   - minimal harness
   - repeated loop for flaky bugs
3. Confirm the loop reproduces the user's actual issue.
4. Rank 3-5 falsifiable hypotheses before testing.
5. Instrument against the predictions of the top hypothesis:
   - debugger or REPL first when practical
   - otherwise targeted logs
   - avoid broad unfocused logging
6. Tighten the loop:
   - faster
   - more deterministic
   - sharper signal
7. Once root cause is confirmed, define the fix and regression check.
8. Re-run the original repro.
9. Remove temporary instrumentation and record the conclusion.

## Investigation Rules

- A reliable feedback loop is the first priority.
- Do not jump to fixes before the bug is reproduced.
- Label conclusions as confirmed, likely, or speculative.
- For flaky bugs, improve reproduction rate instead of waiting for a perfect deterministic repro.
- Tag temporary debug instrumentation clearly so cleanup is easy.
- If no meaningful loop can be built, stop and report what is missing.

## Validation

- Prefer the smallest loop that proves or disproves the hypothesis.
- After approved changes, run:
  - the focused repro
  - any new regression test
  - the smallest relevant validation set for the repo
- Re-run the original scenario before declaring success.

## Outputs / Artifacts

Return:

1. what was used as the feedback loop
2. what reproduced
3. ranked or surviving hypotheses
4. confirmed root cause or best current hypothesis
5. proposed fix or next step
6. blocker or missing dependency when unresolved

When the work is non-trivial, this skill may also write:

- `$ARTIFACTS/<meaningful_id>/analysis_<relevant_name>.md` for new artifacts (see repo `ARTIFACTS.md`; extend existing paths in place)

## Companion Skills

Use this skill as a specialized debugging companion.

Common pairings:

- `repository-technical-analysis` for broader investigation framing
- repository-specific overlay skills for local commands and validation
- contributor skills such as `python-fastapi-contributor` after root cause is clear

## Safety Notes

- Do not broaden scope into general architecture review unless the debugging evidence points there.
- Stop when authenticated inputs fail and the missing access blocks trustworthy debugging.
- Do not leave temporary debug instrumentation behind.
