---
name: python-fastapi-contributor
description: Use this when working on Python or FastAPI code in any repository, including routine implementation, debugging, validation, and pull request or merge request summaries. Covers repo-aware discovery, narrow test selection, failure grouping, and practical validation.
---

# Python FastAPI Contributor

Use this skill for routine engineering work in Python or FastAPI repositories.

## First Read

- Read local contributor docs first when they exist: `AGENTS.md`, `README`, `CONTRIBUTING.md`, `Makefile`, and `pyproject.toml`.
- Prefer repo-native tooling and scripts over ad hoc command variants.
- Keep comments minimal and only explain non-obvious constraints or patterns.
- If the user provides a local workflow artifact such as `task_<issue>.md`, `review_mr_<MR>.md`, or `analysis_mr_<MR>.md`, read it first and reuse its repository, links, assumptions, plan, and open questions before changing code.
- Do not revert unrelated user changes in the worktree.

## Workflow

Use this loop for routine implementation, debugging, or stabilization work:

1. Start from the user's task and any provided local artifact, then identify the local docs, commands, and test targets that govern the repository.
2. Prefer the narrowest test or validation command that exercises the changed area. Expand coverage only when the failure surface is unclear. When rerunning similar work, preserve durable learned sections such as `Validation Lessons`, `Fastest Reliable Test Targets`, `Repo Gotchas`, `Common Failure Shapes`, or `Change Patterns That Broke Tests` when they still match current evidence.
3. When debugging broad failures, group them by root cause before changing code.
4. If the task is framed as investigation, failure analysis, or change planning, propose the intended fix and ask for approval before editing code.
5. Iterate until the change is implemented, the failure set is reduced to a clear blocker, or the repo state shows the next concrete step.

## Validation

- After modifying files, run the relevant lint, format, and test commands for the touched area.
- Prefer maintained repo targets such as `make lint`, `make test`, or project scripts when they exist.
- Use direct tool commands when tighter control is needed or the repo targets are too broad.
- Do not treat full-suite execution as part of the default commit flow unless the task calls for it.
- When a validation step fails to provide useful signal, record it once in `Validation Lessons` or `Fastest Reliable Test Targets` so future reruns can start with a better command.

## Pull Request Summaries

When asked to prepare a pull request or merge request description:

1. Inspect committed changes against the repository's default branch.
2. Read any repo template or contribution guide if present.
3. Produce a concise, fully rendered summary focused on what changed and why.
4. Fill required sections instead of leaving placeholders behind.

## General Notes

- Infer the default branch from the repository; use `main` or `master` as appropriate.
- If `git` or `curl` fails because of authentication or authorization problems, stop immediately and inform the user instead of continuing with incomplete inputs.
- If `git` times out while fetching or pushing resources, stop immediately and inform the user instead of continuing with incomplete inputs.
- When a project also has a repo-specific overlay skill, use both: keep the generic workflow here and let the overlay supply project-local commands and anchors.

## Artifact-Aware Behavior

When a local workflow artifact is provided:

- read it first for durable context and task framing
- reuse its repository path, context links, assumptions, initial plan, and open questions
- still validate decisions against the current code, tests, and repository docs before editing
- preserve the shared core sections from `../ARTIFACTS.md` when updating the same artifact

This is additive only and does not replace the normal repository-aware contributor workflow.

## Self-Improving Behavior

When rerunning implementation, debugging, or stabilization work for the same area:

- read any existing task or analysis artifact first
- preserve durable learned sections such as `## Validation Lessons`, `## Fastest Reliable Test Targets`, `## Repo Gotchas`, `## Common Failure Shapes`, and `## Change Patterns That Broke Tests` when they still match current evidence
- refresh conclusions against the live code, repo docs, and current validation results before reusing them
- promote repeated confirmed observations into short operational heuristics, preferably phrased like `when changing X, run Y first`
- demote, mark stale, or remove heuristics contradicted by new evidence

This keeps contributor artifacts useful across reruns without replacing the normal repo-aware implementation and validation loop.
