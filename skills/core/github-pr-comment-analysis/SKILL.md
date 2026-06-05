---
name: github-pr-comment-analysis
description: >-
  Analyze GitHub pull requests comment-by-comment. Consume PR context from `github`, skip resolved
  threads, group actionable unresolved comments into subsections inside the main PR Markdown artifact
  (prefer `$ARTIFACTS/<meaningful_id>/review_pr_<PR>.md`; use `analysis_pr_<PR>.md` when that file is the working artifact),
  preserve full plan history there, track PR/comment anchors plus proposed solution and reply-waiting
  status, optionally support quick-fix mode for selected grouped issues such as `fix 2 and 5 now`,
  optionally split grouped issues across subagents when explicitly authorized with disjoint subsection
  ownership in the same file, migrate legacy split artifacts into the main file when present,
  and produce a short final report on-screen.
---

# GitHub PR Comment Analysis

Use this skill from a GitHub repository root when the user wants a pull request analyzed comment-by-comment.
Use this skill as a workflow-specific overlay for `github`.

## Single main artifact

**Do not create separate work-plan, per-issue, or consolidated-report Markdown files** (no `work_plan_pr_<PR>.md`, `analysis_pr_<PR>_issue_<NN>.md`, or `pr_<PR>_comment_report.md` for new runs).

Put everything into **one** PR artifact under `$ARTIFACTS/<meaningful_id>/` per repository `ARTIFACTS.md` (default `meaningful_id`: `pr-<PR>` unless a tracker key or repo rule applies; explicit user paths win):

1. Prefer **`$ARTIFACTS/<meaningful_id>/review_pr_<PR>.md`** as the canonical combined bootstrap + grouped-comment workspace.
2. If the session uses **`$ARTIFACTS/<meaningful_id>/analysis_pr_<PR>.md`** instead (investigation-heavy bootstrap or user-provided file only), enrich **that** file with the same grouped-comment sections—do not create a parallel `review_pr_<PR>.md` unless the user asks.

Resolve `<PR>` from live `github` context (`pr_number`) before naming paths. **Legacy:** root-level `review_pr_<PR>.md` or `analysis_pr_<PR>.md` already present remain valid—open and extend them instead of relocating.

## When to Use

Use this skill when the user wants to:

- analyze a GitHub PR comment-by-comment
- group actionable unresolved review threads **inside the main PR artifact**
- preserve grouped-issue history and reply/waiting state in that same file
- run quick-fix analysis for selected grouped issues **by subsection**

## When Not to Use

Do not use this skill when:

- the task is only PR transport access or identity resolution; use `github`
- the task is only local Git repository inspection; use `git`
- the task is primarily repository-specific technical analysis or code changes without grouped PR comment analysis
- the user has not authorized subagents and parallel delegation is the only reason to invoke this skill

## First Read

- Read the repository `AGENTS.md` before running commands.
- Consume normalized PR context from `github`.
- Treat `github` as the transport boundary whether data came from GitHub MCP or fallback `gh` / `gh api`.
- Open or create the **single main artifact** at `$ARTIFACTS/<meaningful_id>/review_pr_<PR>.md` by preference (otherwise `$ARTIFACTS/<meaningful_id>/analysis_pr_<PR>.md`, or an existing legacy root-level file). If missing, bootstrap minimal PR framing consistent with `../ARTIFACTS.md` under `$ARTIFACTS/`, then continue.
- Do not duplicate PR parsing, repository identity resolution, or GitHub transport logic here.
- Use `multi-spawn-agent` only when the user has explicitly authorized subagents or parallel agent work.
- Pair this skill with a repository-specific analysis skill when the user wants code-aware technical conclusions or proposed fixes.

## Inputs

Accept, in order of preference:

- normalized PR context already resolved by `github`
- or an existing local PR artifact (`$ARTIFACTS/…/review_pr_<PR>.md`, `$ARTIFACTS/…/analysis_pr_<PR>.md`, or legacy root-level equivalents)
- or a raw PR number when context already establishes `pull_request`
- or a PR URL
- optional grouped-issue selection (numbered index or stable labels such as `issue_02`)

If starting from a local artifact, read it first, extract canonical `pr_number` and PR link, then refresh through `github` before grouping.

Resolve ambiguity between issue vs PR per `github` rules before fetching.

## Section layout inside the main artifact

Append or refresh grouped-comment material **after** canonical bootstrap sections from `../ARTIFACTS.md`. Use:

```text
## Grouped unresolved comments

Short-lived session index (optional): numbered picks → stable labels (`issue_01`, …).

### issue_01 — <short title>

Stable `### issue_*` headings anchor reruns and quick-fix mode.

For each grouped issue subsection keep:

- stable issue label
- PR link and direct comment/review links when available
- authors
- short problem statement
- short proposed solution when inferable
- reply/waiting status (`answered_waiting_for_author_feedback` when applicable)
- affected files or modules when known
- grouped comment summary
- technical analysis (concise; defer deeper repo analysis to overlays when paired)
- verdict
- proposed changes (high level)
- recommended next action
- confidence and open questions
- optional durable extras on reruns: Follow-up Findings, Improvement Candidates, Reviewer Pattern Notes, Common Fix Shapes, Thread Outcome

Add compact **History** bullets when prior snapshots must remain inspectable.

```

Session numbering lives beside stable headings; subsection slug (`issue_01`) is durable.

## Modes

### Full analysis mode

Default when grouping or refreshing all actionable unresolved threads.

### Quick-fix mode

When scope narrows (`fix 2 and 5`, `issue_03`, …):

- refresh PR threads through `github`
- map picks via session index or regenerate index
- touch only selected `### issue_*` blocks inside `## Grouped unresolved comments`

## Companion Skills

Common pairings:

- `github` for transport and normalized threads
- repository-specific analysis skills for deeper conclusions or patches
- `multi-spawn-agent` only when explicitly authorized

## Workflow

1. Start at repository root.
2. Resolve `pr_number` and `meaningful_id` (default `pr-<PR>`); choose `$ARTIFACTS/<meaningful_id>/review_pr_<PR>.md` vs `$ARTIFACTS/<meaningful_id>/analysis_pr_<PR>.md` per **Single main artifact**, or reuse a legacy root-level file when already present.
3. Read the artifact; keep upstream bootstrap sections coherent.
4. Refresh PR review/conversation state through `github`.
5. Filter to actionable unresolved items unless asked otherwise.
6. Group related threads/comments sharing one issue.
7. If legacy split files exist (`work_plan_pr_<PR>.md`, `analysis_pr_<PR>_issue_*.md`, `pr_<PR>_comment_report.md`), merge durable notes into `### issue_*`, then remove legacy files after successful merge.
8. Upsert `## Grouped unresolved comments` and subsections **only in the main artifact**.
9. Preserve or mark stale bullets intentionally on reruns.
10. Skip automation noise unless requested.
11. Finish with on-screen summary citing the **full path** to the single main artifact (e.g. `$ARTIFACTS/pr-336/review_pr_336.md`).

## Parallel Worker Template

Authorize parallel work only with strict subsection ownership:

```text
Main artifact: $ARTIFACTS/<meaningful_id>/review_pr_<PR>.md (or analysis_pr_<PR>.md when session-scoped; legacy root paths when already open).

Workers edit ONLY assigned ### issue_<label> blocks under ## Grouped unresolved comments.

No edits to other subsections or bootstrap headers.

Serialize if subsection overlap risk exists.

Final screen summary cites the one artifact path.
```

## Selection Resolution Rules

Prefer latest session index inside `## Grouped unresolved comments`; regenerate when ambiguous.

Always map to stable `issue_*` labels before editing.

## Quick-Fix Output

Deliver selections, summaries, next actions, and confirm updates landed in the **single main artifact path**.

## Validation

- Refresh via `github` before rewriting grouped sections.
- Stable `### issue_*` headings across reruns.
- Exactly one PR Markdown carries grouped-comment results unless user directs otherwise.

## Outputs / Artifacts

Creates or updates **only** the single main artifact:

- `$ARTIFACTS/<meaningful_id>/review_pr_<PR>.md` **or** `$ARTIFACTS/<meaningful_id>/analysis_pr_<PR>.md` (preferred for new sessions)
- legacy root-level `review_pr_<PR>.md` or `analysis_pr_<PR>.md` when that file is already the working artifact

Return grouped summaries on-screen plus the artifact’s full path.

## Artifact-Aware Behavior

Remote PR state wins after refresh—never trust cached prose alone.

Preserve core schema sections per `../ARTIFACTS.md`.

Keep transport normalization delegated to `github`; keep grouped-comment prose reviewer-grounded.

## Safety Notes

- Do not fork duplicate GitHub transport logic here.
- Skip resolved threads unless explicitly requested.
- Subagents only when explicitly authorized.
