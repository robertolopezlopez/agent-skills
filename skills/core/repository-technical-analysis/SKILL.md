---
name: repository-technical-analysis
description: Use this when performing technical analysis in a code repository, including test failure investigation, root-cause analysis, architecture inspection, incident debugging, regression triage, or performance analysis. Covers evidence-first investigation, targeted reproduction, root-cause grouping, and concise recommendations.
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

## First Read

- Read local workflow and contributor docs first when they exist: `AGENTS.md`, `README`, `CONTRIBUTING.md`, `Makefile`, and `pyproject.toml`.
- Prefer evidence collection before proposing fixes.
- If the user provides a local workflow artifact such as `task_<issue>.md`, `review_mr_<MR>.md`, or `analysis_mr_<MR>.md`, read it first and reuse its links, assumptions, prior plan, and open questions as investigation anchors.
- Do not edit code until the failure mode or hypothesis is clear enough to defend.

## Workflow

Use this loop for technical analysis tasks:

1. Start from the user's task and gather the repositories, documents, tickets, URLs, or artifacts they provided. Read any local artifact first.
2. Identify the narrowest reliable reproduction. Expand to broader coverage only when the failure surface is still unclear.
3. Use any relevant local material as research input, including repositories, notes, logs, and prior analysis files.
4. Fetch online material when needed, including documentation or API references.
5. Run the tests, scripts, benchmarks, or reproduction steps that best isolate the issue.
6. When rerunning or extending an existing `analysis_<relevant_name>.md`, preserve durable learned sections such as `Follow-up Findings`, `Improvement Candidates`, `Root Cause Lessons`, `Known Patterns`, `Dead Ends Tried`, `Fastest Reliable Repro`, or `Next-Time Checks` when they still match current evidence, explicitly mark stale heuristics, and promote repeated confirmed observations into reusable checks.
7. Write the analysis incrementally to `analysis_<relevant_name>.md` when the investigation is non-trivial.
8. Iterate until the findings are confirmed, reduced to a small set of defensible hypotheses, or blocked by a clearly stated dependency.

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

- `analysis_<relevant_name>.md`

## General Notes

- For reference repositories, switch to the default branch and update them before relying on them.
- When a project also has a repo-specific overlay skill, use both: keep the generic investigation workflow here and let the overlay provide project-local commands, configs, and anchors.

## Companion Skills

Use this skill as the generic investigation layer.

Common pairings:

- repository-specific overlay skills for local commands, configs, and validation
- transport skills such as `jira`, `confluence`, or `gitlab` when the investigation starts from remote issue, wiki, or MR context

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

- read the existing `analysis_<relevant_name>.md` first
- preserve local learned sections such as `## Follow-up Findings`, `## Improvement Candidates`, and optional `## Root Cause Lessons` when they still match current evidence
- preserve optional reusable sections such as `## Known Patterns`, `## Dead Ends Tried`, `## Fastest Reliable Repro`, and `## Next-Time Checks` when they still match current evidence
- refresh live evidence from the repository, logs, tests, traces, and documents before concluding
- keep temporary hypotheses separate from confirmed findings
- promote repeated confirmed observations into short operational heuristics, preferably phrased like `when X, check Y first`
- demote, mark stale, or remove heuristics that new evidence contradicts
- keep learned sections concise, task-local, and evidence-backed rather than generic advice
- update preserved sections only when new evidence supports the change

This makes the analysis artifact durable across reruns without auto-rewriting the skill logic itself.
