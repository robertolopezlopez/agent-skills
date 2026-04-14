---
name: gitlab-mr-comment-analysis
description: "Analyze GitLab merge requests comment-by-comment. Consume MR context from `gitlab`, skip resolved threads, group related actionable unresolved comments into `work_plan_mr_<MR>.md`, preserve full plan history, track MR/comment/analysis links plus proposed solution and reply-waiting status, optionally split grouped issues across subagents when explicitly authorized, clean stale prior-run analysis/report files, and produce a short final report."
---

# GitLab MR Comment Analysis

Use this skill from a GitLab repository root when the user wants an MR analyzed comment-by-comment.
Use this skill as a workflow-specific overlay for `gitlab`.

## First Read

- Read the repository `AGENTS.md` before running commands.
- Consume normalized MR context from `gitlab`.
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

If the input is a local MR artifact, read it first, extract the canonical `mr_iid` and MR link, then refresh live MR context through `gitlab` before comment analysis.
If the input is only a raw MR IID or MR URL, resolve it through `gitlab` first and then continue with this skill.
Extract and reuse the canonical `mr_iid` consistently in filenames and reporting.

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
4. Filter the normalized thread set to actionable unresolved review issues.
5. Group related comments together when they refer to the same underlying issue.
6. Build `work_plan_mr_<MR>.md` with one section per grouped issue. For each grouped issue, record:
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
7. Do not analyze resolved comments.
8. Ignore pure system notes or clearly non-actionable chatter unless the user asks for them.
9. If follow-on analysis will run in parallel and subagents are explicitly authorized, split grouped issues into independent worker scopes using `work_plan_mr_<MR>.md` as the source of truth.
10. Remove stale files from previous runs for the same MR before the final report:
   - remove `mr_<MR>_comment_report.md`
   - remove any `analysis_mr_<MR>_*.md` files that are not linked from the current `work_plan_mr_<MR>.md`
11. Create a consolidated report file named `mr_<MR>_comment_report.md`.
12. Show an on-screen report with 2-3 lines per analyzed grouped issue plus the path to its Markdown file.

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

For the final on-screen report, list each grouped issue with:

- issue label
- 2-3 line summary
- verdict
- short proposed changes summary
- reply/waiting status when relevant
- Markdown file path

## Artifact-Aware Behavior

When the user provides a GitLab bootstrap artifact such as `review_mr_<MR>.md` or `analysis_mr_<MR>.md`:

- read the artifact first for task framing and prior assumptions
- do not trust it as the source of truth for current discussion state
- always refresh live MR comments and thread status through `gitlab` before grouping issues
- keep output filenames based on the canonical live `mr_iid`

This keeps artifact reuse additive while preserving the existing `gitlab`-driven contract for MR identity and thread normalization.
