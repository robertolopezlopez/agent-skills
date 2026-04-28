---
name: gitlab-mr-comment-analysis
description: "Analyze GitLab merge requests comment-by-comment. Consume MR context from `gitlab`, skip resolved threads, group related actionable unresolved comments into `work_plan_mr_<MR>.md`, preserve full plan history, track MR/comment/analysis links plus proposed solution and reply-waiting status, optionally support a quick-fix mode for selected grouped issues such as `fix 2 and 5 now`, optionally split grouped issues across subagents when explicitly authorized, clean stale prior-run analysis/report files, and produce a short final report."
---

# GitLab MR Comment Analysis

Use this skill from a GitLab repository root when the user wants an MR analyzed comment-by-comment.
Use this skill as a workflow-specific overlay for `gitlab`.

## When to Use

Use this skill when the user wants to:

- analyze a GitLab MR comment-by-comment
- group actionable unresolved review comments into issues
- create or refresh `work_plan_mr_<MR>.md`
- create or refresh `mr_<MR>_comment_report.md`
- run quick-fix analysis for selected grouped issues

## When Not to Use

Do not use this skill when:

- the task is only MR transport access or identity resolution; use `gitlab`
- the task is only local Git repository inspection; use `git`
- the task is primarily repository-specific technical analysis or code changes without grouped MR comment analysis
- the user has not authorized subagents and parallel delegation is the only reason to invoke this skill

## First Read

- Read the repository `AGENTS.md` before running commands.
- Consume normalized MR context from `gitlab`.
- Treat `gitlab` as the transport boundary. Consume its normalized MR context whether it came from GitLab MCP or fallback `glab` / `glab api`.
- If the user provides a local MR artifact such as `review_mr_<MR>.md` or `analysis_mr_<MR>.md`, read it first and reuse its MR link, repository, assumptions, and open questions as bootstrap context.
- Do not duplicate MR parsing, project identity resolution, or GitLab transport logic here.
- Use `multi-spawn-agent` only when the user has explicitly authorized subagents or parallel agent work.
- Pair this skill with a repository-specific analysis skill when the user wants code-aware technical conclusions or proposed fixes.

## Inputs

Accept, in order of preference:

- normalized MR context already resolved by `gitlab`
- or a local MR artifact such as `review_mr_<MR>.md` or `analysis_mr_<MR>.md`
- or a raw MR IID like `123`
- or an MR URL that contains the IID
- optional grouped-issue selection from the current session, such as:
  - numbered grouped issues from the latest on-screen summary
  - stable grouped issue labels like `issue_02`

If the input is a local MR artifact, read it first, extract the canonical `mr_iid` and MR link, then refresh live MR context through `gitlab` before comment analysis.
If the input is only a raw MR IID or MR URL, resolve it through `gitlab` first and then continue with this skill.
Extract and reuse the canonical `mr_iid` consistently in filenames and reporting.

## Modes

Use one of two modes:

### Full analysis mode

Default when the user asks to analyze an MR, review unresolved comments, group issues, or produce artifacts.

### Quick-fix mode

Use when the user explicitly asks to address only specific grouped issues, for example:

- `fix 2 and 5`
- `address issue_03`
- `handle only issues 1 and 4`

Quick-fix mode should:

- refresh live MR context through `gitlab`
- resolve the selected grouped issues against the latest grouped summary
- limit analysis to the selected grouped issues
- avoid rebuilding the full MR report unless the user asks for a full rerun
- hand off only the selected grouped issues to the repository-specific companion workflow when technical conclusions or code changes are needed

## Companion Skills

Use this skill as the workflow and grouping layer on top of `gitlab`.

Common pairings:

- `gitlab` for transport, MR identity, thread state, and comment-link normalization
- repository-specific analysis skills for code-aware conclusions or proposed fixes
- `multi-spawn-agent` only when the user has explicitly authorized subagents or parallel work

## Workflow

1. Start in the target repository root.
2. If a local MR artifact was provided, read it first and preserve any useful bootstrap context such as repository path, assumptions, prior plan notes, or open questions.
3. Refresh and consume live MR context resolved by `gitlab`, including:
   - `mr_iid`
   - `mr_link`
   - project reference
   - normalized threads and comments
   - direct comment links when available
   - thread status such as actionable unresolved thread, resolved thread, and `answered_waiting_for_author_feedback`
   - without depending on whether `gitlab` used GitLab MCP or fallback `glab`
4. Filter the normalized thread set to actionable unresolved review issues.
5. Group related comments together when they refer to the same underlying issue.
6. Build a stable session-local numbered summary for grouped issues after grouping is complete.
   - Use numbering only as a user-selection convenience layer for the current session.
   - Do not replace stable issue labels such as `issue_01` in artifacts.
   - When the user later says `fix 2 and 5`, resolve those numbers against the latest numbered grouped-issue summary in the current session.
7. If prior `work_plan_mr_<MR>.md` or `analysis_mr_<MR>_issue_<NN>.md` files already exist, preserve durable learned sections such as `Follow-up Findings`, `Improvement Candidates`, `Reviewer Pattern Notes`, `Common Fix Shapes`, and `Thread Outcome` for still-matching unresolved grouped issues, explicitly mark stale patterns, and promote repeated confirmed reviewer themes into reusable heuristics.
8. Build `work_plan_mr_<MR>.md` with one section per grouped issue. For each grouped issue, record:
   - a stable issue label such as `issue_01`
   - one or more comment labels such as `comment_01`, `comment_02`
   - author
   - short problem statement
   - short proposed solution statement when inferable from the thread
   - comment status, including whether you have already answered and are waiting for feedback from the comment author
   - affected file or module when known
   - MR link
   - direct MR comment link for each included comment when available
   - analysis file link such as `analysis_mr_<MR>_issue_01.md`
   - a history section that keeps prior plan states instead of replacing them with only the latest snapshot
9. If the user selects specific grouped issues by session-local number or stable issue label:
   - resolve the selection against the refreshed grouped issue set
   - map each selected number to its stable issue label
   - analyze only the selected grouped issues
   - skip unrelated unresolved grouped issues
   - avoid rebuilding unrelated per-issue files unless the user asks for a full rerun
10. Do not analyze resolved comments.
11. Ignore pure system notes or clearly non-actionable chatter unless the user asks for them.
12. If follow-on analysis will run in parallel and subagents are explicitly authorized, split grouped issues into independent worker scopes using `work_plan_mr_<MR>.md` as the source of truth.
13. Remove stale files from previous runs for the same MR before the final report:
   - remove `mr_<MR>_comment_report.md`
   - remove any `analysis_mr_<MR>_*.md` files that are not linked from the current `work_plan_mr_<MR>.md`
14. Create a consolidated report file named `mr_<MR>_comment_report.md` unless quick-fix mode is active and the user asked for selected grouped issues only.
15. Show an on-screen report with 2-3 lines per analyzed grouped issue plus the path to its Markdown file.
    - In full analysis mode, number each grouped issue in the on-screen summary.
    - In quick-fix mode, show the selected session-local numbers and their mapped stable issue labels.

## Worker Requirements

Each grouped-issue analysis must:

- only cover actionable unresolved comments assigned in `work_plan_mr_<MR>.md`
- record whether you have already replied and are waiting for feedback from the comment author
- write one Markdown file per assigned grouped issue
- leave repository-specific technical analysis and proposed code changes to the companion skill for that repository

Use this per-issue file shape:

```text
analysis_mr_<MR>_issue_<NN>.md
```

Each file should contain:

1. MR and issue label
2. MR link
3. direct MR comment links when available
4. reply status, including `answered_waiting_for_author_feedback` when applicable
5. grouped comment summary
6. affected files or modules
7. technical analysis
8. verdict
9. proposed changes
10. recommended next action
11. confidence and open questions
12. optional follow-up findings
13. optional improvement candidates
14. optional reviewer pattern notes
15. optional common fix shapes
16. optional thread outcome

## Parallel Worker Template

When subagents are allowed, use a `work_plan_mr_<MR>.md`-driven split like this:

```text
Use gitlab-mr-comment-analysis plus the repository-specific companion skills.

Read work_plan_mr_<MR>.md first.

Spawn N parallel worker agents with fork_context: true, where N is based on the number of independent actionable unresolved grouped issues.

For each worker:
- read work_plan_mr_<MR>.md
- own exactly the grouped issues assigned in `work_plan_mr_<MR>.md`
- create the assigned analysis_mr_<MR>_issue_<NN>.md files
- do not modify other workers' analysis files
- apply the repository-specific analysis workflow for the assigned issues
- return: summary, files changed, and validation run

After all workers finish:
- remove stale `analysis_mr_<MR>_*.md` and `mr_<MR>_comment_report.md` files from previous runs that are not part of the current plan
- create `mr_<MR>_comment_report.md`
- show a screen summary with 2-3 lines per grouped issue and the corresponding Markdown path
```

## Selection Resolution Rules

When the user refers to grouped issues by number:

1. Prefer the numbering from the latest on-screen grouped-issue summary in the current session.
2. If numbering is stale, missing, or ambiguous, regenerate a fresh numbered grouped-issue summary before proceeding.
3. Resolve each selected number to its stable issue label such as `issue_02`.
4. Use the stable issue label in filenames, artifacts, and follow-on analysis.

When the user refers to grouped issues by stable label such as `issue_03`, use that label directly.

## Quick-Fix Output

In quick-fix mode, the minimum output is:

1. selected grouped-issue numbers or labels
2. mapped stable issue labels
3. short problem summary per selected grouped issue
4. proposed change summary
5. recommended next action
6. paths to any updated analysis files

Do not regenerate `mr_<MR>_comment_report.md` or unrelated issue files unless the user asks for a full MR refresh.

## Reporting

Create `mr_<MR>_comment_report.md` with:

1. MR identifier
2. list of analyzed grouped issues
3. one short section per grouped issue
4. link or path to each `analysis_mr_<MR>_issue_<NN>.md`
5. overall themes, repeated failure modes, or shared root causes when known

For `work_plan_mr_<MR>.md`, include:

1. MR identifier and MR link
2. one entry per actionable unresolved grouped issue
3. direct MR comment links for all comments included in each grouped issue when available
4. short proposed solution statement for each grouped issue
5. reply/waiting status for each grouped issue, including whether you are waiting for author feedback
6. analysis file link for each grouped issue
7. status tracking for each analysis
8. a running history log that preserves previous plan states instead of replacing them
9. optional follow-up findings for grouped issues that persist across reruns
10. optional improvement candidates for grouped issues or repeated reviewer themes
11. optional reviewer pattern notes for repeated author preferences or recurring review themes
12. optional common fix shapes for issues that repeatedly resolve in the same way
13. optional thread outcome for grouped issues that were later accepted, redirected, or superseded

For the final on-screen report, list each grouped issue with:

- session-local grouped-issue number
- issue label
- 2-3 line summary
- verdict
- short proposed changes summary
- reply/waiting status when relevant
- Markdown file path

In quick-fix mode, the on-screen report may be limited to the selected grouped issues only.

## Validation

- Always refresh live MR comments and thread status through `gitlab` before grouping issues.
- Keep grouped-issue numbering session-local and map it back to stable issue labels in artifacts.
- Exclude resolved comments unless the user explicitly asks for them.
- Keep filenames, issue labels, and report structure stable across reruns.

## Outputs / Artifacts

This skill may create or update:

- `work_plan_mr_<MR>.md`
- `analysis_mr_<MR>_issue_<NN>.md`
- `mr_<MR>_comment_report.md`

It should also return:

- grouped-issue summaries
- issue-number to stable-label mappings
- selected issue paths in quick-fix mode
- reply/waiting status when relevant

## Artifact-Aware Behavior

When the user provides a GitLab bootstrap artifact such as `review_mr_<MR>.md` or `analysis_mr_<MR>.md`:

- read the artifact first for task framing and prior assumptions
- do not trust it as the source of truth for current discussion state
- always refresh live MR comments and thread status through `gitlab` before grouping issues
- keep output filenames based on the canonical live `mr_iid`

This keeps artifact reuse additive while preserving the existing `gitlab`-driven contract for MR identity and thread normalization.
When enriching an existing bootstrap artifact, preserve the shared core sections documented in `../ARTIFACTS.md`.
When rerunning analysis for the same MR, preserve local learned sections such as `Follow-up Findings`, `Improvement Candidates`, `Reviewer Pattern Notes`, `Common Fix Shapes`, and `Thread Outcome` for unresolved grouped issues that still match the refreshed live MR context.
Keep learned sections short, operational, and tied to observed reviewer behavior rather than generic advice.
When the same reviewer or theme repeats, prefer heuristics phrased like `when reviewer flags X, verify Y before replying`.
Keep grouped-issue analysis, filenames, and report structure transport-agnostic so downstream artifacts stay stable when `gitlab` switches between MCP and fallback transport.

## Safety Notes

- Do not duplicate GitLab transport or project-resolution logic here; consume it from `gitlab`.
- Do not analyze resolved comments unless the user asks for them.
- Use `multi-spawn-agent` only when subagents are explicitly authorized.
