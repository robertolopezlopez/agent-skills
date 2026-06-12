---
name: gitlab-mr-comment-analysis
description: >-
  Analyze GitLab merge requests comment-by-comment. Consume MR context from `gitlab`, skip resolved
  threads, group actionable unresolved comments into subsections inside the main MR Markdown artifact
  (prefer `$ARTIFACTS/<meaningful_id>/review_mr_<MR>.md`; use `$ARTIFACTS/<meaningful_id>/analysis_mr_<MR>.md` when that file is the working artifact),
  preserve full plan history there, track MR/comment/analysis anchors plus proposed solution and
  reply-waiting status, optionally support quick-fix mode for selected grouped issues such as
  `fix 2 and 5 now`, optionally split grouped issues across subagents when explicitly authorized with
  disjoint subsection ownership in the same file, migrate legacy split artifacts into the main file when present,
  and produce a short final report on-screen.
---

# GitLab MR Comment Analysis

Use this skill from a GitLab repository root when the user wants an MR analyzed comment-by-comment.
Use this skill as a workflow-specific overlay for `gitlab`.

## Single main artifact

**Do not create separate work-plan, per-issue, or consolidated-report Markdown files** (no `work_plan_mr_<MR>.md`, `analysis_mr_<MR>_issue_<NN>.md`, or `mr_<MR>_comment_report.md` for new runs).

Put everything into **one** MR artifact under `$ARTIFACTS/<meaningful_id>/` per repository `ARTIFACTS.md` (default `meaningful_id`: `mr-<MR>` unless a tracker key or repo rule applies; explicit user paths win):

1. Prefer **`$ARTIFACTS/<meaningful_id>/review_mr_<MR>.md`** as the canonical combined bootstrap + grouped-comment workspace.
2. If the session uses **`$ARTIFACTS/<meaningful_id>/analysis_mr_<MR>.md`** instead (investigation-heavy bootstrap or user-provided file only), enrich **that** file with the same grouped-comment sections—do not create a parallel `review_mr_<MR>.md` unless the user asks.

Resolve `<MR>` from live `gitlab` context (`mr_iid`) before naming paths. **Legacy:** root-level `review_mr_<MR>.md` or `analysis_mr_<MR>.md` already present remain valid—open and extend them instead of relocating.

## When to Use

Use this skill when the user wants to:

- analyze a GitLab MR comment-by-comment
- group actionable unresolved review comments into issues **inside the main MR artifact**
- preserve grouped-issue history and reply/waiting state in that same file
- run quick-fix analysis for selected grouped issues **by subsection**

## When Not to Use

Do not use this skill when:

- the task is only MR transport access or identity resolution; use `gitlab`
- the task is only local Git repository inspection; use synced **`GIT-ACCESS.md`**
- the task is primarily repository-specific technical analysis or code changes without grouped MR comment analysis
- the user has not authorized subagents and parallel delegation is the only reason to invoke this skill

## First Read

- Read the repository `AGENTS.md` before running commands.
- Consume normalized MR context from `gitlab`.
- Treat `gitlab` as the transport boundary whether data came from local `glab` / `glab api` or GitLab MCP.
- Open or create the **single main artifact** at `$ARTIFACTS/<meaningful_id>/review_mr_<MR>.md` by preference (otherwise `$ARTIFACTS/<meaningful_id>/analysis_mr_<MR>.md`, or an existing legacy root-level file). If missing, bootstrap minimal MR framing consistent with `../ARTIFACTS.md` under `$ARTIFACTS/`, then continue.
- Do not duplicate MR parsing, project identity resolution, or GitLab transport logic here.
- Use `multi-spawn-agent` only when the user has explicitly authorized subagents or parallel agent work.
- Pair this skill with a repository-specific analysis skill when the user wants code-aware technical conclusions or proposed fixes.

## Inputs

Accept, in order of preference:

- normalized MR context already resolved by `gitlab`
- or an existing local MR artifact (`$ARTIFACTS/…/review_mr_<MR>.md`, `$ARTIFACTS/…/analysis_mr_<MR>.md`, or legacy root-level equivalents)
- or a raw MR IID like `123`
- or an MR URL that contains the IID
- optional grouped-issue selection from the current session (numbered summary or stable labels like `issue_02`)

If the input is a local MR artifact, read it first, extract the canonical `mr_iid` and MR link, then refresh live MR context through `gitlab` before comment analysis.
If the input is only a raw MR IID or MR URL, resolve it through `gitlab` first.
Reuse `mr_iid` consistently in the chosen artifact filename.

## Section layout inside the main artifact

Append or refresh grouped-comment material **after** the canonical bootstrap sections from `../ARTIFACTS.md` (preserve core section order). Use this heading scaffold:

```text
## Grouped unresolved comments

Short-lived session index (optional): numbered list mapping session picks → stable labels (`issue_01`, …).

### issue_01 — <short title>

Use stable headings (`issue_01`, `issue_02`, …) so reruns and quick-fix mode stay anchored.

For each grouped issue subsection, keep:

- stable issue label (repeat in body if helpful)
- MR link and direct MR comment links for each included thread when available
- authors
- short problem statement
- short proposed solution statement when inferable
- reply/waiting status (`answered_waiting_for_author_feedback` when applicable)
- affected files or modules when known
- grouped comment summary
- technical analysis (keep concise here; delegate deeper repo-specific analysis to overlay skills when paired)
- verdict
- proposed changes (high level)
- recommended next action
- confidence and open questions
- optional durable extras when reruns justify them: Follow-up Findings, Improvement Candidates, Reviewer Pattern Notes, Common Fix Shapes, Thread Outcome

Include under each issue or at section bottom a compact **History** bullet trail when prior snapshots matter instead of deleting older reasoning outright.

```

Use numbering only as a **session-local** selection aid inside `## Grouped unresolved comments`; stable subsection headings (`### issue_01`) are the durable anchors.

## Modes

### Full analysis mode

Default when the user asks to analyze an MR, review unresolved comments, group issues, or refresh grouped-comment sections.

### Quick-fix mode

Use when the user explicitly narrows scope (`fix 2 and 5`, `address issue_03`, …):

- refresh live MR context through `gitlab`
- map selections to stable labels using the latest session index in the artifact or regenerate that index first
- update **only** the selected subsections inside `## Grouped unresolved comments`
- avoid rewriting unrelated issues unless the user asks for a full rerun

## Companion Skills

Use this skill as the workflow and grouping layer on top of `gitlab`.

Common pairings:

- `gitlab` for transport, MR identity, thread state, and comment-link normalization
- repository-specific analysis skills for code-aware conclusions or proposed fixes
- `multi-spawn-agent` only when explicitly authorized

## Workflow

1. Start in the target repository root.
2. Resolve `mr_iid` and `meaningful_id` (default `mr-<MR>`); choose `$ARTIFACTS/<meaningful_id>/review_mr_<MR>.md` vs `$ARTIFACTS/<meaningful_id>/analysis_mr_<MR>.md` per **Single main artifact**, or reuse a legacy root-level file when already present.
3. Read the main artifact; preserve bootstrap assumptions and prior notes outside grouped-comment sections when still valid.
4. Refresh MR discussion state through `gitlab` (threads, links, resolved vs actionable).
5. Filter to actionable unresolved review threads unless the user asks otherwise.
6. Group related comments that share one underlying issue.
7. If legacy split files exist for this IID (`work_plan_mr_<MR>.md`, `analysis_mr_<MR>_issue_*.md`, `mr_<MR>_comment_report.md`), merge durable content into the matching `### issue_*` subsections (then delete those legacy files if the merge succeeded).
8. Upsert `## Grouped unresolved comments` and each `### issue_*` subsection in the **main artifact only**.
9. Preserve durable learned bullets inside matching subsections when reruns still apply; mark superseded material explicitly instead of silent deletion.
10. Ignore pure system notes or clearly non-actionable chatter unless the user asks for them.
11. Show an on-screen summary (2–3 lines per grouped issue, stable labels, **full path** to the single main artifact, e.g. `$ARTIFACTS/mr-1447/review_mr_1447.md`).

## Parallel Worker Template

When subagents are explicitly authorized, parallelize by **subsection ownership** in the same file:

```text
Use gitlab-mr-comment-analysis plus repository-specific companion skills.

Main artifact: $ARTIFACTS/<meaningful_id>/review_mr_<MR>.md (or $ARTIFACTS/<meaningful_id>/analysis_mr_<MR>.md if that is the session artifact).

Read the full file once for context.

Spawn N workers (fork_context: true) for independent grouped issues.

Each worker:
- edits ONLY its assigned `### issue_<label>` subsection inside ## Grouped unresolved comments
- does not modify other issue subsections or unrelated bootstrap sections
- returns summary plus confirmation of the single artifact path

Merge conflicts are unacceptable: serialize writers when subsection boundaries cannot stay disjoint.

After workers finish:
- refresh session index inside ## Grouped unresolved comments if needed
- produce one screen summary pointing at the single main artifact path
```

## Selection Resolution Rules

When the user refers to grouped issues by number, prefer the latest session index in `## Grouped unresolved comments`; if stale or missing, regenerate before resolving.

Map selections to stable labels (`issue_02`) and operate on those subsections only.

## Quick-Fix Output

Minimum: selected labels, short summaries, proposed change takeaway, next action, **path to the single main artifact** updated on disk.

## Validation

- Refresh live MR threads through `gitlab` before updating grouped sections.
- Keep stable `### issue_*` headings across reruns.
- One Markdown file per MR for grouped-comment artifacts unless the user explicitly chooses otherwise.

## Outputs / Artifacts

Creates or updates **only**:

- `$ARTIFACTS/<meaningful_id>/review_mr_<MR>.md` **or** `$ARTIFACTS/<meaningful_id>/analysis_mr_<MR>.md` (exactly one chosen main artifact per run series; legacy root-level paths when already in use)

Also returns grouped-issue summaries, mappings, and reply/waiting notes on-screen.

## Artifact-Aware Behavior

Bootstrap artifacts are not authoritative for live thread state—always refresh through `gitlab` before merging grouped-comment edits.

When enriching the artifact, preserve shared core sections per `../ARTIFACTS.md`.

Keep grouped-comment prose reviewer-specific and operational (`when reviewer flags X, verify Y before replying`).

## Safety Notes

- Do not duplicate GitLab transport or project-resolution logic here; consume it from `gitlab`.
- Do not analyze resolved threads unless the user asks for them.
- Use `multi-spawn-agent` only when explicitly authorized.
