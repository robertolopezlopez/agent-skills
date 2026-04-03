---
name: private-service-mr-comment-analysis
description: "Use when working in the private-service repository and the user wants a GitLab merge request reviewed comment-by-comment. Fetch the merge request with glab using the user-provided MR parameter, read the MR comments and discussion threads, skip resolved comments, create a work_plan_mr_<MR>.md file for the unresolved comment split with MR, comment, analysis links, a short proposed solution statement, and whether you have already replied and are waiting for feedback from the comment author, use multi-spawn-agent to analyze comments in parallel when subagents are explicitly authorized, use repository-technical-analysis together with private-service-technical-analysis for each unresolved comment, write one Markdown analysis file per comment including the relevant MR comment link and reply/waiting status, and finish with a short on-screen report summarizing each analysis file."
---

# Guided Experience Service MR Comment Analysis

Use this skill from the `private-service` repository root when the user wants an MR analyzed comment-by-comment.

## First Read

- Read `AGENTS.md` before running commands.
- Use `glab` to fetch the merge request and its comment threads.
- Use `repository-technical-analysis` together with `private-service-technical-analysis` for the actual technical analysis.
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
4. Build `work_plan_mr_<MR>.md` with one section per actionable unresolved review comment. For each comment, record:
   - a stable comment label such as `comment_01`
   - author
   - short problem statement
   - short proposed solution statement
   - comment status, including whether you have already answered and are waiting for feedback from the comment author
   - affected file or module when known
   - MR link
   - direct MR comment link when available
   - analysis file path or link such as `analysis_mr_<MR>_comment_01.md`
5. Do not analyze resolved comments.
6. Ignore pure system notes or clearly non-actionable chatter unless the user asks for them.
7. When an unresolved thread already contains your reply after the author's comment and there is no follow-up from the author yet, mark it as `answered_waiting_for_author_feedback`.
8. If subagents are explicitly authorized, use `multi-spawn-agent` and spawn one worker per independent comment or per small disjoint group of comments.
9. Each worker must use `repository-technical-analysis` plus `private-service-technical-analysis`, read `work_plan_mr_<MR>.md`, own only its assigned comment scope, and write the assigned Markdown analysis file.
10. If subagents are not authorized, analyze the comments sequentially with the same workflow and output files.
11. After all workers finish, create a consolidated report file named `mr_<MR>_comment_report.md`.
12. Show an on-screen report with 2-3 lines per analyzed comment plus the path to its Markdown file.

## Worker Requirements

Each comment analysis must:

- identify whether the comment appears valid, partially valid, outdated, or blocked by missing context
- inspect the relevant local code, tests, and nearby modules before concluding
- note missing prerequisites, environment gaps, or follow-up checks when they materially affect the conclusion
- record whether you have already replied and are waiting for feedback from the comment author
- only cover unresolved comments assigned in `work_plan_mr_<MR>.md`
- write one Markdown file per assigned comment

Use this per-comment file shape:

```text
analysis_mr_<MR>_comment_<NN>.md
```

Each file should contain:

1. MR and comment label
2. MR link
3. direct MR comment link when available
4. reply status, including `answered_waiting_for_author_feedback` when applicable
5. original comment summary
6. affected files or modules
7. technical analysis
8. verdict
9. recommended next action
10. confidence and open questions

## Parallel Worker Template

When subagents are allowed, use a `work_plan_mr_<MR>.md`-driven split like this:

```text
Use multi-spawn-agent, repository-technical-analysis, and private-service-technical-analysis.

Read work_plan_mr_<MR>.md first.

Spawn N parallel worker agents with fork_context: true, where N is based on the number of independent actionable unresolved comments.

For each worker:
- read work_plan_mr_<MR>.md
- use repository-technical-analysis and private-service-technical-analysis
- own exactly the comments assigned in work_plan_mr_<MR>.md
- create the assigned analysis_mr_<MR>_comment_<NN>.md files
- do not modify other workers' analysis files
- return: summary, files changed, and validation run

After all workers finish:
- create mr_<MR>_comment_report.md
- show a screen summary with 2-3 lines per comment and the corresponding Markdown path
```

## Reporting

Create `mr_<MR>_comment_report.md` with:

1. MR identifier
2. list of analyzed comments
3. one short section per comment
4. link or path to each `analysis_mr_<MR>_comment_<NN>.md`
5. overall themes, repeated failure modes, or shared root causes

For `work_plan_mr_<MR>.md`, include:

1. MR identifier and MR link
2. one entry per actionable unresolved comment
3. direct MR comment link for each comment when available
4. short proposed solution statement for each comment
5. reply/waiting status for each comment, including whether you are waiting for author feedback
6. analysis file path or link for each comment
7. status tracking for each analysis

For the final on-screen report, list each comment with:

- comment label
- 2-3 line summary
- verdict
- reply/waiting status when relevant
- Markdown file path

## Useful Repo Anchors

- `AGENTS.md` for repo workflow rules
- `Makefile` for standard commands
- `pyproject.toml` for pytest markers and project config
- `cicd/scripts/set_weaviate_config.sh` when analysis depends on production Weaviate settings
