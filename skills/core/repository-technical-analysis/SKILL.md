---
name: repository-technical-analysis
description: Use this when performing technical analysis in a code repository, including test failure investigation, root-cause analysis, architecture inspection, incident debugging, regression triage, or performance analysis. Covers evidence-first investigation, targeted reproduction, root-cause grouping, and concise recommendations. Uses the fast-grep companion for speed-ordered literal codebase search. Non-trivial analysis writes to `$ARTIFACTS/<meaningful_id>/analysis_<relevant_name>.md` by default; legacy root-level analysis files remain valid.
---

# Repository Technical Analysis

Use this skill for investigation-first work across repositories.

## When to Use

Use this skill when the user wants:

- root-cause analysis
- test failure investigation
- incident or regression triage
- architecture inspection tied to a concrete problem
- evidence-backed technical recommendations

## When Not to Use

Do not use this skill when:

- the task is primarily remote transport access like Jira or GitLab fetch
- a repository-specific overlay alone already fully defines the needed workflow
- the user only wants code changes with no meaningful investigation component

## Inputs

- Accept an optional output file path (absolute or relative).
- Accept an optional `meaningful_id` or tracker key when the user provides one.
- Accept an optional local workflow artifact such as `$ARTIFACTS/…/task_<issue>.md`, `review_mr_<MR>.md`, or `analysis_mr_<MR>.md`.
- If the user provides an output file, use it.
- If the user does not provide one and the investigation is non-trivial, write under `$ARTIFACTS/<meaningful_id>/` per repository `ARTIFACTS.md`:
  - default basename: `analysis_<relevant_name>.md` (ticket slug, failure surface, branch topic, or similar)
  - default `meaningful_id`: tracker key from a provided task artifact or user input when present; else `pr-<n>` / `mr-<iid>` when PR/MR context is clear; else a sanitized branch or topic slug aligned with `<relevant_name>`
- **Legacy:** an existing root-level `analysis_<relevant_name>.md` (or other user path) already present remains valid—open and extend it instead of relocating unless the user asks to migrate.

## First Read

- Read local workflow and contributor docs first when they exist: `AGENTS.md`, `README`, `CONTRIBUTING.md`, `Makefile`, and `pyproject.toml`.
- Literal codebase search: workflow **step 3** via the **`fast-grep`** companion (details live in `fast-grep/SKILL.md` only).
- When investigation needs JSON filtering, run **`scripts/check_skill_prereqs.sh investigate`** for optional `jq`.
- Prefer evidence collection before proposing fixes.
- If the user provides a local workflow artifact, read it first and reuse its links, assumptions, prior plan, and open questions as investigation anchors.
- Do not edit code until the failure mode or hypothesis is clear enough to defend.

## Workflow

Use this loop for technical analysis tasks:

1. Start from the user's task and gather the repositories, documents, tickets, URLs, or artifacts they provided. Read any local artifact first.
2. Identify the narrowest reliable reproduction. Expand to broader coverage only when the failure surface is still unclear.
3. **Repository code search** — when you need literal anchors in the codebase (failure strings, symbols, imports, feature flags, config keys):
   - Follow **`fast-grep`** end to end: resolve tools with **`fast-grep/scripts/fast-grep-resolve`**, ask before installing missing **`rg`**, **`ugrep`**, or **`ag`**, then run **`fast-grep/scripts/fast-grep`**.
   - Tighten scope with **`path`** and **`glob`** (for example the failing package, `*.test.ts`, or `src/auth/`) instead of searching the whole monorepo first.
   - Use **SemanticSearch** only when the target is behavioral or naming is uncertain; confirm candidates with **`fast-grep`** or file reads.
   - Record the search tool used (`rg`, `ag`, `agent-grep`, …) in the analysis artifact when it materially affects confidence or reproducibility.
4. Use any relevant local material as research input, including repositories, notes, logs, and prior analysis files.
5. Fetch online material when needed, including documentation or API references.
6. Run the tests, scripts, benchmarks, or reproduction steps that best isolate the issue.
7. When rerunning or extending an existing analysis artifact (`$ARTIFACTS/…/analysis_<relevant_name>.md` by preference, or a legacy root-level file when already in use), preserve durable learned sections such as `Follow-up Findings`, `Improvement Candidates`, `Root Cause Lessons`, `Known Patterns`, `Dead Ends Tried`, `Fastest Reliable Repro`, or `Next-Time Checks` when they still match current evidence, explicitly mark stale heuristics, and promote repeated confirmed observations into reusable checks.
8. Write the analysis incrementally to `$ARTIFACTS/<meaningful_id>/analysis_<relevant_name>.md` when the investigation is non-trivial and no explicit or legacy path is already in use.
9. Iterate until the findings are confirmed, reduced to a small set of defensible hypotheses, or blocked by a clearly stated dependency.

## Investigation Rules

- Prefer targeted reproduction after the first broad run.
- Verify assumptions against the code before making architectural claims.
- Call out whether a conclusion is confirmed, likely, or still speculative.
- When multiple failures share one cause, report the shared cause once and list the impact clearly.
- When a tactic fails to produce useful signal, record it once in `Dead Ends Tried` with a short reason so future reruns can skip it.
- Keep recommendations concrete: what should change, why, and how confident the evidence is.
- If `git` or `curl` fails because of authentication or authorization problems, stop immediately and inform the user instead of continuing with incomplete inputs.
- If `git` times out while fetching or pushing resources, stop immediately and inform the user instead of continuing with incomplete inputs.

## Validation

- Use repo commands where practical, but prefer direct commands when tighter control is needed.
- For codebase text search during analysis, validate that **`fast-grep`** (or its documented agent fallback) was used instead of unbounded manual file walks.
- After approved code changes, run the lint, format, and test commands that are relevant to the fix.
- Prefer the smallest validation set that proves or disproves the hypothesis before expanding coverage.

## Outputs / Artifacts

Technical analysis output should usually include:

1. What was run
2. What failed or regressed
3. The most likely root cause or competing hypotheses
4. The proposed fix or next step
5. Any blocker, missing dependency, or uncertainty

When the work is non-trivial, this skill may also write or enrich:

- `$ARTIFACTS/<meaningful_id>/analysis_<relevant_name>.md` for new runs (legacy root-level `analysis_<relevant_name>.md` paths remain valid when already in use)

## General Notes

- For reference repositories, switch to the default branch and update them before relying on them.
- When a project also has a repo-specific overlay skill, use both: keep the generic investigation workflow here and let the overlay provide project-local commands, configs, and anchors.

## Companion Skills

Use this skill as the generic investigation layer.

- **`fast-grep`** — required for step 3 (workflow owner for search prose)

Common pairings:

- repository-specific overlay skills for local commands, configs, and validation
- transport skills such as `jira`, `confluence`, or `gitlab` when the investigation starts from remote issue, wiki, or MR context
- `diagnose` when a concrete bug repro is already known and the work shifts from scoping to instrumentation

## Artifact-Aware Behavior

When a local workflow artifact is provided:

- read it first for context, prior assumptions, and open questions
- reuse its links and previously captured plan as investigation input
- still treat current code, logs, tests, and reproductions as the source of truth
- preserve the shared core sections from `../ARTIFACTS.md` when enriching the same artifact

This is additive only and does not replace the normal evidence-first analysis workflow.

## Safety Notes

- Do not edit code until the failure mode or hypothesis is clear enough to defend.
- Stop when critical authenticated inputs such as `git` or `curl` access fail and tell the user.
- Keep conclusions labeled as confirmed, likely, or speculative.

## Self-Improving Behavior

When rerunning analysis for the same problem or artifact:

- read the existing analysis artifact first (`$ARTIFACTS/…/analysis_<relevant_name>.md` by preference, or a legacy root-level file when that is where prior work lives)
- preserve local learned sections such as `## Follow-up Findings`, `## Improvement Candidates`, and optional `## Root Cause Lessons` when they still match current evidence
- preserve optional reusable sections such as `## Known Patterns`, `## Dead Ends Tried`, `## Fastest Reliable Repro`, and `## Next-Time Checks` when they still match current evidence
- refresh live evidence from the repository, logs, tests, traces, and documents before concluding
- keep temporary hypotheses separate from confirmed findings
- promote repeated confirmed observations into short operational heuristics, preferably phrased like `when X, check Y first`
- demote, mark stale, or remove heuristics that new evidence contradicts
- keep learned sections concise, task-local, and evidence-backed rather than generic advice
- update preserved sections only when new evidence supports the change

This makes the analysis artifact durable across reruns without auto-rewriting the skill logic itself.
