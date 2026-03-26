---
name: private-service-contributor
description: Use this when working in the private-service repository on Python or FastAPI code, contributor workflows, validation, or merge request summaries. Covers repo-specific rules for uv usage, lint and format commands, selective test execution, optional Weaviate environment setup, and how to prepare MR descriptions against origin/main.
---

# Guided Experience Service Contributor

Use this skill for routine engineering work in this repository.

## First Read

- Read `AGENTS.md` before making changes.
- Use `uv` for Python commands and scripts.
- Keep comments minimal and only explain non-standard patterns or constraints.
- Do not revert unrelated user changes in the worktree.

## Workflow

Use this loop for broad debugging or stabilization work:

1. Run unit and integration tests with 10 workers to surface failures quickly. Prefer `uv run pytest -v -m "not integration and not functional" -n 10` and `uv run pytest -v -m "integration and not skip_ci" -n 10` because the current `Makefile` targets do not expose worker count. If the repo targets are updated to support parallelism, use `make test-unit` and `make test-integration` with 10 workers instead.
2. Analyze the failing tests and group errors by root cause before proposing code changes.
3. Propose the intended fix and ask for approval before editing code when the task is framed as investigation, failure analysis, or change planning.
4. Iterate until the failure set is resolved or reduced to a clearly explained blocker.

## Validation

- After modifying files, run `make lint`.
- Run `make format` when formatting is needed or when lint indicates formatting drift.
- Run tests manually only when they are relevant to the task. Do not treat full test execution as part of the default commit flow.

Prefer these commands:

- `make lint`
- `make format`
- `uv run pytest -v -m "not integration and not functional" -n 10`
- `uv run pytest -v -m "integration and not skip_ci" -n 10`
- `uv run pytest -v tests/<target>`

## Environment Notes

- If the task needs production Weaviate settings, source `cicd/scripts/set_weaviate_config.sh` before running the relevant commands.
- The primary Python version is defined in `pyproject.toml`.
- Repo automation is exposed through `Makefile`; prefer those targets over ad hoc command variants when they exist.

## Merge Request Summaries

When asked to prepare an MR description:

1. Inspect only committed changes on the current branch against `origin/main`.
2. Read `.gitlab/merge_request_templates/Default.md`.
3. Produce a fully rendered, copy-pasteable version of that template.
4. Fill every section with concise engineer-oriented content.
5. Tick affected subproject checkboxes based on touched files.
6. Focus on what changed and why, not on repeating obvious file paths.

## Useful Repo Anchors

- `AGENTS.md` for local contributor rules
- `Makefile` for lint, format, and test targets
- `pyproject.toml` for Python, pytest, and ruff configuration
- `.gitlab/merge_request_templates/Default.md` for MR descriptions
