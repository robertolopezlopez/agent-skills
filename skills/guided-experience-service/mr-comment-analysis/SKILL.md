---
name: guided-experience-service-mr-comment-analysis
description: Analyze unresolved guided-experience-service MR comments, enriching grouped issue subsections in the main artifact with repository-specific evidence and proposed changes.
---

# Guided Experience Service MR Comment Analysis

Use this skill from the `guided-experience-service` repository root when the user wants an MR analyzed comment-by-comment.
This skill consumes upstream GitLab MR context and **`gitlab-mr-comment-analysis`** grouped-comment layout **inside** `$ARTIFACTS/<meaningful_id>/review_mr_<MR>.md` or `$ARTIFACTS/<meaningful_id>/analysis_mr_<MR>.md`, then deepens each `### issue_*` subsection with service-specific technical analysis, verdicts, and proposed changes.

## When to Use

Use this skill when the user wants unresolved MR review comments analyzed for the `guided-experience-service` repository and needs:

- grouped issue analysis grounded in local repo code
- guided-experience-service-specific verdicts and risks
- proposed changes written **into the same main MR artifact** under each issue subsection

## When Not to Use

Do not use this skill when:

- the task is only GitLab transport access or generic grouping; use `gitlab` or `gitlab-mr-comment-analysis`
- the task is outside the `guided-experience-service` repository
- the task is general repo investigation with no grouped MR comment workflow

## First Read

- Read `AGENTS.md` before running commands.
- Read `gitlab` to resolve normalized MR context (identity, links, discussions, thread status).
- Read `gitlab-mr-comment-analysis` so grouping conventions (`## Grouped unresolved comments`, stable `### issue_*` headings) stay consistent.
- Treat `gitlab` + `gitlab-mr-comment-analysis` as transport and grouping boundaries whether upstream used local `glab` or GitLab MCP.
- Pair `repository-technical-analysis` with `guided-experience-service-technical-analysis` for technical conclusions.
- After technical analysis for an issue subsection, use `guided-experience-service-contributor` to add concrete proposed changes **in that subsection**.
- Use `multi-spawn-agent` only when explicitly authorized.

## Inputs

Accept, in order of preference:

- `review_mr_<MR>.md` or `analysis_mr_<MR>.md` under `$ARTIFACTS/<meaningful_id>/` (default `meaningful_id`: `mr-<MR>`) that already contains `## Grouped unresolved comments` from `gitlab-mr-comment-analysis`, or legacy root-level equivalents already in use
- MR context from `gitlab` when grouping sections still need refresh or creation upstream
- raw MR IID / MR URL → resolve via `gitlab`, run **`gitlab-mr-comment-analysis`** to populate grouped sections in the main artifact before repo-specific enrichment

If `$ARTIFACTS/…/review_mr_<MR>.md`, `$ARTIFACTS/…/analysis_mr_<MR>.md`, or a legacy root-level equivalent exists, read it first, then refresh live MR state through `gitlab` before editing grouped sections.

## Companion Skills

- `gitlab`, `gitlab-mr-comment-analysis`
- `repository-technical-analysis`, `guided-experience-service-technical-analysis`
- `guided-experience-service-contributor`
- `multi-spawn-agent` only when explicitly authorized

## Workflow

1. Start in the `guided-experience-service` repository root.
2. Identify the **single main artifact** (`$ARTIFACTS/<meaningful_id>/review_mr_<MR>.md` preferred; else `$ARTIFACTS/<meaningful_id>/analysis_mr_<MR>.md`, or an existing legacy root-level file) per `gitlab-mr-comment-analysis` rules.
3. If grouped sections are missing, run upstream `gitlab` → `gitlab-mr-comment-analysis` to create/update `## Grouped unresolved comments` and `### issue_*` blocks **in that file**.
4. Refresh MR threads through `gitlab`; reconcile subsection labels with live unresolved threads.
5. For **each** `### issue_*` subsection under `## Grouped unresolved comments`, use `repository-technical-analysis` plus `guided-experience-service-technical-analysis` to inspect local code, tests, and nearby modules before concluding.
6. After technical analysis for that subsection, run `guided-experience-service-contributor` sequentially (same worker) to append or refine **Proposed changes** (and related bullets) **inside the same subsection**.
7. If subagents are authorized, assign disjoint `### issue_*` subsections to workers; forbid cross-editing other subsections or bootstrap headers.
8. If subagents are not authorized, process subsections sequentially.
9. Finish with a concise on-screen summary (2–3 lines per issue) plus the **full path** to the single main artifact (e.g. `$ARTIFACTS/mr-1447/review_mr_1447.md`).
10. On reruns, preserve durable repo-local bullets (`Reviewer Preference Notes`, `Common Service Fix Patterns`, `Environment Preconditions`, `Thread Outcome`) inside matching subsections when still valid.

## Worker Requirements

Each grouped-issue subsection must:

- judge whether the comment is valid, partially valid, outdated, or blocked by missing context
- inspect relevant local code/tests before concluding
- note prerequisites, environment gaps, or follow-up checks when material
- record reply/waiting status when relevant
- expand **only** the assigned `### issue_*` region inside `## Grouped unresolved comments`
- run `guided-experience-service-contributor` after technical analysis to deepen proposed changes inside that subsection

Do **not** create standalone `analysis_mr_<MR>_issue_<NN>.md` files for new work.

## Parallel Worker Template

```text
Use gitlab-mr-comment-analysis plus repository-technical-analysis, guided-experience-service-technical-analysis, guided-experience-service-contributor, and optionally multi-spawn-agent.

Main artifact: $ARTIFACTS/<meaningful_id>/review_mr_<MR>.md (or $ARTIFACTS/<meaningful_id>/analysis_mr_<MR>.md when session-scoped).

Ensure ## Grouped unresolved comments exists with ### issue_* anchors.

Spawn N workers only when authorized.

Each worker:
- edits ONLY its assigned ### issue_<label> subsection
- runs guided-experience-service-contributor after technical analysis within that subsection
- avoids touching sibling issue subsections or bootstrap sections

After workers finish: summarize on-screen with the single artifact path.
```

## Boundaries

- GitLab transport stays in `gitlab`; grouping layout stays aligned with `gitlab-mr-comment-analysis`.
- Do not duplicate raw regrouping when subsection anchors already match refreshed MR context unless upstream rerun was requested.
- Prefer merging legacy split artifacts upstream (`gitlab-mr-comment-analysis`) before layering service-specific depth here.

## Artifact-Aware Behavior

When local bootstrap artifacts exist:

- read first for assumptions and open questions
- refresh MR context through `gitlab` before trusting discussion excerpts
- preserve core sections per `../ARTIFACTS.md`

## Self-Improving Behavior

On reruns for the same MR:

- read existing grouped sections first
- preserve durable service-local heuristics when refreshed MR state + code still support them
- refresh via upstream flows before reusing lessons

## Reporting

Each `### issue_*` subsection should end up containing:

- guided-experience-service-specific technical analysis
- verdict grounded in inspection
- proposed changes (via contributor discipline)
- prerequisites/blockers when relevant

## Validation

- Consume refreshed grouped sections before concluding.
- Ground verdicts in code/tests/environment facts.

## Outputs / Artifacts

Updates **only** the chosen main MR artifact under `$ARTIFACTS/<meaningful_id>/` (`review_mr_<MR>.md` or `analysis_mr_<MR>.md`, or a legacy root-level path when already in use), enriching grouped-issue subsections in place.

## Safety Notes

- No standalone duplicate MR artifact contracts.
- Use `multi-spawn-agent` only when explicitly authorized.

## Useful Repo Anchors

- `AGENTS.md` for repo workflow rules
- `Makefile` for standard commands
- `pyproject.toml` for pytest markers and project config
- `cicd/scripts/set_weaviate_config.sh` when analysis depends on production Weaviate settings
