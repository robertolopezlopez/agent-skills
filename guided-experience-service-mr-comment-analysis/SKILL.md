---
name: private-service-mr-comment-analysis
description: "Use when working in the private-service repository and the user wants a GitLab merge request reviewed comment-by-comment. Fetch the merge request with glab using the user-provided MR parameter, read the MR comments and discussion threads, skip resolved comments, create a work_plan_mr_<MR>.md file that preserves full plan history, groups related unresolved comments, and records MR, comment, and analysis links, a short proposed solution statement, and whether you have already replied and are waiting for feedback from the comment author, use multi-spawn-agent to analyze comments or grouped issues in parallel when subagents are explicitly authorized, use repository-technical-analysis together with private-service-technical-analysis for each unresolved comment group, then use private-service-contributor to update each analysis file with proposed changes, remove stale analysis and report files from previous runs for the same MR, and finish with a short on-screen report summarizing each analysis file."
---

# Guided Experience Service MR Comment Analysis

Use this skill from the `private-service` repository root when the user wants an MR analyzed comment-by-comment.

## First Read

- Read `AGENTS.md` before running commands.
- Use `glab` to fetch the merge request and its comment threads.
- Use `repository-technical-analysis` together with `private-service-technical-analysis` for the actual technical analysis.
- After each technical analysis is complete, use `private-service-contributor` to add concrete proposed changes to the grouped-issue analysis file.
- Use `multi-spawn-agent` only when the user has explicitly authorized subagents or parallel agent work.

## Inputs

Require a merge request parameter:

- MR IID like `123`
- or an MR URL that contains the IID

Extract the IID first and use that single value consistently in filenames and reporting.

## Workflow

1. Start in the `private-service` repository root.
2. Read the MR overview and comments with `glab mr view <MR> --comments`.
3. If needed, use `glab api` to inspect structured discussion data for the same MR.
4. Build `work_plan_mr_<MR>.md` with one section per actionable unresolved review issue. Group similar comments together when they refer to the same underlying issue. For each grouped issue, record:
   - a stable issue label such as `issue_01`
   - one or more comment labels such as `comment_01`, `comment_02`
   - author
   - short problem statement
   - short proposed solution statement
   - comment status, including whether you have already answered and are waiting for feedback from the comment author
   - affected file or module when known
   - MR link
   - direct MR comment link for each included comment when available
   - analysis file link such as `analysis_mr_<MR>_issue_01.md`
   - a history section that keeps prior plan states instead of replacing them with only the latest snapshot
5. Do not analyze resolved comments.
6. Ignore pure system notes or clearly non-actionable chatter unless the user asks for them.
7. When an unresolved thread already contains your reply after the author's comment and there is no follow-up from the author yet, mark it as `answered_waiting_for_author_feedback`.
8. If subagents are explicitly authorized, use `multi-spawn-agent` and spawn one worker per independent grouped issue or per small disjoint set of grouped issues.
9. Each worker must use `repository-technical-analysis` plus `private-service-technical-analysis`, read `work_plan_mr_<MR>.md`, own only its assigned grouped issue scope, and write the assigned Markdown analysis file.
10. If subagents are not authorized, analyze the grouped issues sequentially with the same workflow and output files.
11. After its technical analysis, each worker runs `private-service-contributor` sequentially to add proposed changes to its analysis file.
12. After all workers finish and before creating the final report, remove stale files from previous runs for the same MR:
   - remove `mr_<MR>_comment_report.md`
   - remove any `analysis_mr_<MR>_*.md` files that are not linked from the current `work_plan_mr_<MR>.md`
13. Create a consolidated report file named `mr_<MR>_comment_report.md`.
14. Show an on-screen report with 2-3 lines per analyzed grouped issue plus the path to its Markdown file.

## Worker Requirements

Each grouped-issue analysis must:

- identify whether the comment appears valid, partially valid, outdated, or blocked by missing context
- inspect the relevant local code, tests, and nearby modules before concluding
- note missing prerequisites, environment gaps, or follow-up checks when they materially affect the conclusion
- record whether you have already replied and are waiting for feedback from the comment author
- only cover unresolved comments assigned in `work_plan_mr_<MR>.md`
- write one Markdown file per assigned grouped issue
- after the technical analysis section is complete, use `private-service-contributor` sequentially in the same worker to add a proposed changes section to the same file

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
Use multi-spawn-agent, repository-technical-analysis, private-service-technical-analysis, and private-service-contributor.

Read work_plan_mr_<MR>.md first.

Spawn N parallel worker agents with fork_context: true, where N is based on the number of independent actionable unresolved grouped issues.

For each worker:
- read work_plan_mr_<MR>.md
- use repository-technical-analysis and private-service-technical-analysis
- after the technical analysis is complete, use private-service-contributor sequentially in the same worker to update the same analysis file with proposed changes
- own exactly the comments assigned in work_plan_mr_<MR>.md
- create the assigned analysis_mr_<MR>_issue_<NN>.md files
- do not modify other workers' analysis files
- return: summary, files changed, and validation run

After all workers finish:
- remove stale `analysis_mr_<MR>_*.md` and `mr_<MR>_comment_report.md` files from previous runs that are not part of the current plan
- create mr_<MR>_comment_report.md
- show a screen summary with 2-3 lines per comment and the corresponding Markdown path
```

## Reporting

Create `mr_<MR>_comment_report.md` with:

1. MR identifier
2. list of analyzed grouped issues
3. one short section per grouped issue
4. link or path to each `analysis_mr_<MR>_issue_<NN>.md`
5. overall themes, repeated failure modes, or shared root causes

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

## Useful Repo Anchors

- `AGENTS.md` for repo workflow rules
- `Makefile` for standard commands
- `pyproject.toml` for pytest markers and project config
- `cicd/scripts/set_weaviate_config.sh` when analysis depends on production Weaviate settings
