---
name: private-service-technical-analysis
description: Use this with repository-technical-analysis when performing technical analysis in the private-service repository. Adds repo-specific uv usage, pytest commands, Weaviate setup, and local investigation anchors.
---

# Guided Experience Service Technical Analysis

Use this skill as a repo-specific overlay for `repository-technical-analysis`.

## When to Use

Use this skill when the user is doing investigation-first work in the `private-service` repository and needs:

- repo-specific reproduction commands
- repo-specific investigation anchors
- repo-specific Weaviate guidance
- repo-specific analysis artifact expectations

## When Not to Use

Do not use this skill when:

- the task is outside the `private-service` repository
- the generic `repository-technical-analysis` workflow is sufficient with no repo-local rules needed
- the task is primarily transport access such as Jira or GitLab fetch

## First Read

- Read `AGENTS.md` before starting.
- Use `uv` for Python commands and scripts.
- Load `repository-technical-analysis` for the general investigation workflow and reporting structure. Keep this skill focused on repo-local rules.
- If the user provides a local artifact such as `task_<issue>.md`, `review_mr_<MR>.md`, or `analysis_mr_<MR>.md`, read it first and reuse its links, assumptions, prior plan, and open questions as investigation anchors.

## Repo Workflow

- For broad reproduction, start with `uv run pytest -v -m "not integration and not functional" -n 10` and `uv run pytest -v -m "integration and not skip_ci" -n 10`.
- For narrower reproduction, use the smallest `uv run pytest ...` command that still reproduces the issue.
- When the analysis depends on production Weaviate behavior, source `cicd/scripts/set_weaviate_config.sh` first.
- Create `analysis_<relevant_name>.md`, `analysis_<relevant_name>_slides.html`, and `analysis_<relevant_name>_slides_notes.md` when the investigation requires a written artifact or presentation.
- When rerunning similar analysis, preserve durable repo-local learned sections such as `Known Failure Modes`, `Weaviate Pitfalls`, `Fastest Reliable Repro`, and `Next-Time Checks` when they still match current evidence.

## Repo Investigation Rules

- If `git` or `curl` fails because of authentication or authorization problems, stop immediately and inform the user instead of continuing with incomplete inputs.
- If `git` times out while fetching or pushing resources, stop immediately and inform the user instead of continuing with incomplete inputs.
- When a repo-specific tactic fails to provide useful signal, record it once in `Known Failure Modes` or `Weaviate Pitfalls` with the shortest useful reason.

## Repo Validation

- Use `Makefile` targets when they match the task; use direct `uv run pytest ...` commands when tighter control is needed.
- Run `make lint` after code changes are approved and implemented.
- Run `make format` when formatting drift is introduced.

## Validation

- Prefer the smallest reproduction or analysis command that still proves the issue.
- Use repo-native `Makefile` targets when they match the task, but switch to direct `uv run pytest ...` commands when tighter control is needed.
- Reconfirm conclusions against current repo state, test output, and environment setup before closing the investigation.
- Record better reproduction or validation shortcuts when a default command proves noisy or low-signal.

## Environment Notes

- Pytest markers and ruff settings are defined in `pyproject.toml`.

## Artifact-Aware Behavior

When a local workflow artifact is provided:

- read it first for context and previously captured assumptions
- reuse relevant links, repo context, and open questions
- still reproduce issues from current code and test evidence before concluding
- preserve the shared core sections from `../ARTIFACTS.md` when enriching the same artifact

This is additive only and does not replace the normal `repository-technical-analysis` workflow.

## Outputs / Artifacts

This skill may produce or enrich:

- `analysis_<relevant_name>.md`
- `analysis_<relevant_name>_slides.html`
- `analysis_<relevant_name>_slides_notes.md`

It should also provide repo-specific:

- reproduction choices
- environment prerequisites
- validation guidance

## Self-Improving Behavior

When rerunning investigation for the same repo area or failure mode:

- read any existing analysis artifact first
- preserve durable repo-local learned sections such as `## Known Failure Modes`, `## Weaviate Pitfalls`, `## Fastest Reliable Repro`, and `## Next-Time Checks` when they still match current evidence
- refresh conclusions against the live code, pytest output, environment state, and current repo docs before reusing them
- promote repeated confirmed observations into short repo-local heuristics, preferably phrased like `when X fails in private-service, check Y first`
- demote, mark stale, or remove heuristics contradicted by new evidence

This keeps repo-specific investigation artifacts useful across reruns without replacing the base `repository-technical-analysis` workflow.

## Companion Skills

Common pairings:

- `repository-technical-analysis` for the generic investigation workflow
- `private-service-contributor` when investigation leads to approved implementation work
- `gitlab` or `jira` when the investigation starts from remote MR or issue context

## Safety Notes

- Keep this skill focused on repo-local investigation guidance; do not duplicate the base analysis workflow unnecessarily.
- Stop when authenticated `git` or `curl` access fails instead of continuing with partial context.
- Reproduce from live code and test evidence before concluding.

## Useful Repo Anchors

- `repository-technical-analysis` for the generic investigation workflow
- `AGENTS.md` for repo workflow rules
- `Makefile` for standard lint, format, and test targets
- `pyproject.toml` for pytest markers and ruff configuration
- `cicd/scripts/set_weaviate_config.sh` for production Weaviate settings
