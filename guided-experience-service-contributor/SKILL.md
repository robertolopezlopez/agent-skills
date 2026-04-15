---
name: private-service-contributor
description: Use this with python-fastapi-contributor when working in the private-service repository. Adds repo-specific uv usage, lint and format commands, pytest commands, optional Weaviate setup, and merge request summary rules against origin/main.
---

# Guided Experience Service Contributor

Use this skill as a repo-specific overlay for `python-fastapi-contributor`.

## First Read

- Read `AGENTS.md` before making changes.
- Use `uv` for Python commands and scripts.
- Load `python-fastapi-contributor` for the general workflow and validation loop. Keep this skill focused on repo-local rules.
- If the user provides a local artifact such as `task_<issue>.md`, `review_mr_<MR>.md`, or `analysis_mr_<MR>.md`, read it first and reuse its repository, links, assumptions, plan, and open questions before inspecting code.

## Repo Workflow

- For broad debugging or stabilization, start with `uv run pytest -v -m "not integration and not functional" -n 10` and `uv run pytest -v -m "integration and not skip_ci" -n 10` because the current `Makefile` targets do not expose worker count.
- If the repo targets are updated to support parallelism, prefer `make test-unit` and `make test-integration` with 10 workers instead.
- For targeted validation, prefer `uv run pytest -v tests/<target>`.
- When rerunning similar work, preserve durable repo-local learned sections such as `Validation Shortcuts`, `Common Integration Breakpoints`, `Weaviate Setup Lessons`, and `Fastest Reliable Test Targets` when they still match current evidence.

## Repo Validation

- After modifying files, run `make lint`.
- Run `make format` when formatting is needed or when lint indicates formatting drift.
- Use the pytest commands above when repo targets are too broad.
- When a validation command proves noisy, flaky, or low-signal, record it once in `Validation Shortcuts` or `Fastest Reliable Test Targets` with the better alternative.

## Environment Notes

- If the task needs production Weaviate settings, source `cicd/scripts/set_weaviate_config.sh` before running the relevant commands.
- The primary Python version is defined in `pyproject.toml`.
- Repo automation is exposed through `Makefile`; prefer those targets over ad hoc command variants when they exist.
- Before using any existing repository in `~/workspace` as a reference, switch it to `main` and pull the latest changes. If the repository uses `master` instead, switch to `master` and pull there.
- If `git` or `curl` fails because of authentication or authorization problems, stop immediately and inform the user instead of continuing with incomplete inputs.
- If `git` times out while fetching or pushing resources, stop immediately and inform the user instead of continuing with incomplete inputs.

## Merge Request Summaries

When asked to prepare an MR description:

1. Inspect only committed changes on the current branch against `origin/main`.
2. Read `.gitlab/merge_request_templates/Default.md`.
3. Produce a fully rendered, copy-pasteable version of that template.
4. Fill every section with concise engineer-oriented content.
5. Tick affected subproject checkboxes based on touched files.
6. Focus on what changed and why, not on repeating obvious file paths.

## Artifact-Aware Behavior

When a local workflow artifact is provided:

- read it first for task framing and durable context
- reuse its repository path, context links, assumptions, initial plan, and open questions
- refresh local code and test evidence before making implementation decisions
- preserve the shared core sections from `../ARTIFACTS.md` when updating the same artifact

This is additive only and does not replace the normal `python-fastapi-contributor` workflow.

## Self-Improving Behavior

When rerunning implementation, debugging, or stabilization work in this repository:

- read any existing task or analysis artifact first
- preserve durable repo-local learned sections such as `## Validation Shortcuts`, `## Common Integration Breakpoints`, `## Weaviate Setup Lessons`, and `## Fastest Reliable Test Targets` when they still match current evidence
- refresh implementation decisions against the live code, repo docs, and current validation output before reusing them
- promote repeated confirmed observations into short repo-local heuristics, preferably phrased like `when changing X in private-service, run Y first`
- demote, mark stale, or remove heuristics contradicted by new evidence

This keeps repo-specific contributor artifacts useful across reruns without replacing the base `python-fastapi-contributor` workflow.

## Useful Repo Anchors

- `python-fastapi-contributor` for the generic implementation workflow
- `AGENTS.md` for local contributor rules
- `Makefile` for lint, format, and test targets
- `pyproject.toml` for Python, pytest, and ruff configuration
- `.gitlab/merge_request_templates/Default.md` for MR descriptions
