---
name: guided-experience-service-contributor
description: Implement guided-experience-service changes with python-fastapi-contributor, repo-specific `uv`/pytest/lint/format commands, optional Weaviate, MR summaries, dependency injection, and no hidden globals.
---

# Guided Experience Service Contributor

Use this skill as a repo-specific overlay for `python-fastapi-contributor`.

## When to Use

Use this skill when the user is working in the `guided-experience-service` repository and needs:

- repo-specific implementation workflow
- repo-specific validation commands
- repo-specific MR summary rules
- repo-specific Weaviate setup guidance

## When Not to Use

Do not use this skill when:

- the task is outside the `guided-experience-service` repository
- the generic `python-fastapi-contributor` workflow is sufficient with no repo-local rules needed
- the task is primarily transport access such as Jira or GitLab fetch

## First Read

- Read `AGENTS.md` before making changes.
- Use `uv` for Python commands and scripts.
- Load `python-fastapi-contributor` for the general workflow and validation loop. Keep this skill focused on repo-local rules.
- If the user provides a local artifact such as `task_<issue>.md`, `review_mr_<MR>.md`, or `analysis_mr_<MR>.md`, read it first and reuse its repository, links, assumptions, plan, and open questions before inspecting code.

## Design principles

Follow **`python-fastapi-contributor`** and repo **`AGENTS.md`** (**Contributor design principles**):

- inject Weaviate clients, HTTP adapters, and settings — do not add module-level clients or read env vars inside handlers/services
- route and service tests should use fakes or test containers already used in the repo before adding integration-only coverage
- when touching existing singletons or `lru_cache` config helpers, prefer passing explicit deps into the code under change
- for new behavior or regressions, pair with **`tdd`**: red-green-refactor on public interfaces using injected fakes

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
- After validation passes, shrink the diff per **`python-fastapi-contributor`** workflow step 6 before finishing or preparing an MR summary.

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

## Outputs / Artifacts

This skill should usually produce:

- repo-specific command and validation choices
- repo-specific implementation guidance layered on top of `python-fastapi-contributor`
- repo-specific MR summary guidance when requested

When local workflow artifacts are in use, this skill may also enrich:

- `task_<issue>.md`
- `review_mr_<MR>.md`
- `analysis_mr_<MR>.md`

## Self-Improving Behavior

When rerunning implementation, debugging, or stabilization work in this repository:

- read any existing task or analysis artifact first
- preserve durable repo-local learned sections such as `## Validation Shortcuts`, `## Common Integration Breakpoints`, `## Weaviate Setup Lessons`, and `## Fastest Reliable Test Targets` when they still match current evidence
- refresh implementation decisions against the live code, repo docs, and current validation output before reusing them
- promote repeated confirmed observations into short repo-local heuristics, preferably phrased like `when changing X in guided-experience-service, run Y first`
- demote, mark stale, or remove heuristics contradicted by new evidence

This keeps repo-specific contributor artifacts useful across reruns without replacing the base `python-fastapi-contributor` workflow.

## Companion Skills

Common pairings:

- `python-fastapi-contributor` for the generic implementation and validation loop
- `repository-technical-analysis` for investigation-heavy work
- `guided-experience-service-technical-analysis` for repo-specific investigation overlays

## Safety Notes

- Keep this skill focused on repo-local behavior; do not duplicate generic contributor guidance unnecessarily.
- Stop when authenticated `git` or `curl` access fails instead of continuing with partial context.
- Prefer repo-native commands and `uv` workflows over ad hoc alternatives.

## Useful Repo Anchors

- `python-fastapi-contributor` for the generic implementation workflow
- `AGENTS.md` for local contributor rules
- `Makefile` for lint, format, and test targets
- `pyproject.toml` for Python, pytest, and ruff configuration
- `.gitlab/merge_request_templates/Default.md` for MR descriptions
