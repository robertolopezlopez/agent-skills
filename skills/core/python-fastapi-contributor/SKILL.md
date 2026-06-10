---
name: python-fastapi-contributor
description: Use this when working on Python or FastAPI code in any repository, including routine implementation, debugging, validation, and pull request or merge request summaries. Covers repo-aware discovery, narrow test selection, failure grouping, and practical validation.
---

# Python FastAPI Contributor

Use this skill for routine engineering work in Python or FastAPI repositories.

## When to Use

Use this skill when the user wants:

- routine implementation in a Python or FastAPI repository
- debugging or stabilization work in a Python service
- targeted validation after code changes
- a pull request or merge request summary for Python/FastAPI work

## When Not to Use

Do not use this skill when:

- the task is primarily remote transport access such as Jira or GitLab fetch
- the task is primarily investigation-first root-cause analysis better handled by `repository-technical-analysis`
- a repo-specific overlay already fully defines the required local workflow and this generic layer adds no value

## First Read

- Read local contributor docs first when they exist: `AGENTS.md`, `README`, `CONTRIBUTING.md`, `Makefile`, and `pyproject.toml`.
- When locating modules, routes, tests, imports, or error strings in the tree, follow synced **`LITERAL-CODE-SEARCH.md`** (host CLI + **`fast-grep.env`**; agent Grep tool as last resort).
- Prefer repo-native tooling and scripts over ad hoc command variants.
- Keep comments minimal and only explain non-obvious constraints or patterns.
- If the user provides a local workflow artifact such as `$ARTIFACTS/<meaningful_id>/task_<issue>.md`, `review_mr_<MR>.md`, or `analysis_mr_<MR>.md` (or legacy root-level equivalents), read it first and reuse its repository, links, assumptions, plan, and open questions before changing code.
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

## Outputs / Artifacts

This skill should usually produce:

1. implemented code changes or a clear blocker
2. targeted validation results
3. concise summary of what changed and why
4. pull request or merge request text when requested

When a local workflow artifact is being used, this skill may also enrich files under `$ARTIFACTS/<meaningful_id>/` (see repo `ARTIFACTS.md` for `meaningful_id` and basenames):

- `task_<issue>.md`
- `review_mr_<MR>.md`
- `analysis_mr_<MR>.md`

## General Notes

- Infer the default branch from the repository; use `main` or `master` as appropriate.
- If `git` or `curl` fails because of authentication or authorization problems, stop immediately and inform the user instead of continuing with incomplete inputs.
- If `git` times out while fetching or pushing resources, stop immediately and inform the user instead of continuing with incomplete inputs.
- When a project also has a repo-specific overlay skill, use both: keep the generic workflow here and let the overlay supply project-local commands and anchors.

## Companion Skills

Common pairings:

- repo-specific overlay skills for local commands, defaults, and validation
- `repository-technical-analysis` when the task is investigation-heavy before implementation
- transport skills such as `jira`, `confluence`, or `gitlab` when the work starts from remote issue, wiki, or MR context

## Artifact-Aware Behavior

When a local workflow artifact is provided:

- prefer `$ARTIFACTS/<meaningful_id>/` for new artifacts; open and extend existing root-level files in place unless the user asks to migrate
- read it first for durable context and task framing
- reuse its repository path, context links, assumptions, initial plan, and open questions
- still validate decisions against the current code, tests, and repository docs before editing
- preserve the shared core sections from `../ARTIFACTS.md` when updating the same artifact

This is additive only and does not replace the normal repository-aware contributor workflow.

## Safety Notes

- Do not revert unrelated user changes in the worktree.
- If the task is framed as investigation or change planning, ask for approval before editing code.
- Stop when authenticated `git` or `curl` access fails instead of continuing with partial context.

## Self-Improving Behavior

When rerunning implementation, debugging, or stabilization work for the same area:

- read any existing task or analysis artifact first
- preserve durable learned sections such as `## Validation Lessons`, `## Fastest Reliable Test Targets`, `## Repo Gotchas`, `## Common Failure Shapes`, and `## Change Patterns That Broke Tests` when they still match current evidence
- refresh conclusions against the live code, repo docs, and current validation results before reusing them
- promote repeated confirmed observations into short operational heuristics, preferably phrased like `when changing X, run Y first`
- demote, mark stale, or remove heuristics contradicted by new evidence

This keeps contributor artifacts useful across reruns without replacing the normal repo-aware implementation and validation loop.
