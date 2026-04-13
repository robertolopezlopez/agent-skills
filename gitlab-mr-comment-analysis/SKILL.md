---
name: gitlab-mr-comment-analysis
description: "Analyze GitLab merge requests comment-by-comment. Use when given an MR IID or URL and asked to fetch comments with glab, skip resolved threads, group related unresolved comments into work_plan_mr_<MR>.md, preserve full plan history, track MR/comment/analysis links plus proposed solution and reply-waiting status, optionally split grouped issues across subagents when explicitly authorized, clean stale prior-run analysis/report files, and produce a short final report."
---

# GitLab MR Comment Analysis

Use this skill from a GitLab repository root when the user wants an MR analyzed comment-by-comment.
Use this skill as a workflow-specific overlay for `gitlab`.

## First Read

- Read the repository `AGENTS.md` before running commands.
- Use the generic `gitlab` skill for MR fetch, discussion inspection, IID extraction, direct link handling, and resolved-vs-unresolved thread handling.
- Use `multi-spawn-agent` only when the user has explicitly authorized subagents or parallel agent work.
- Pair this skill with a repository-specific analysis skill when the user wants code-aware technical conclusions or proposed fixes.

## Inputs

Require a merge request parameter:

- MR IID like `123`
- or an MR URL that contains the IID

Extract the IID first and use that single value consistently in filenames and reporting.

## Workflow

1. Start in the target repository root.
2. Follow the generic `gitlab` skill workflow to fetch the MR overview, inspect comments, and inspect structured discussions when needed.
3. Build `work_plan_mr_<MR>.md` with one section per actionable unresolved review issue. Group similar comments together when they refer to the same underlying issue. For each grouped issue, record:
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
4. Do not analyze resolved comments.
5. Ignore pure system notes or clearly non-actionable chatter unless the user asks for them.
6. When an unresolved thread already contains your reply after the author's comment and there is no follow-up from the author yet, mark it as `answered_waiting_for_author_feedback`.
7. If follow-on analysis will run in parallel and subagents are explicitly authorized, split grouped issues into independent worker scopes using `work_plan_mr_<MR>.md` as the source of truth.
8. Remove stale files from previous runs for the same MR before the final report:
   - remove `mr_<MR>_comment_report.md`
   - remove any `analysis_mr_<MR>_*.md` files that are not linked from the current `work_plan_mr_<MR>.md`
9. Create a consolidated report file named `mr_<MR>_comment_report.md`.
10. Show an on-screen report with 2-3 lines per analyzed grouped issue plus the path to its Markdown file.

## Worker Requirements

Each grouped-issue analysis must:

- only cover unresolved comments assigned in `work_plan_mr_<MR>.md`
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
- own exactly the comments assigned in work_plan_mr_<MR>.md
- create the assigned analysis_mr_<MR>_issue_<NN>.md files
- do not modify other workers' analysis files
- apply the repository-specific analysis workflow for the assigned issues
- return: summary, files changed, and validation run

After all workers finish:
- remove stale `analysis_mr_<MR>_*.md` and `mr_<MR>_comment_report.md` files from previous runs that are not part of the current plan
- create `mr_<MR>_comment_report.md`
- show a screen summary with 2-3 lines per comment and the corresponding Markdown path
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
