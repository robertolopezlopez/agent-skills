---
name: private-service-mr-comment-analysis
description: "Analyze private-service merge request comments by combining gitlab-mr-comment-analysis with private-service-specific technical analysis. Use when given an MR IID or URL and asked to analyze unresolved review comments in private-service, using repository-technical-analysis with private-service-technical-analysis for each grouped issue and private-service-contributor to add proposed changes."
---

# Guided Experience Service MR Comment Analysis

Use this skill from the `private-service` repository root when the user wants an MR analyzed comment-by-comment.

## First Read

- Read `AGENTS.md` before running commands.
- Read `gitlab` first for the generic GitLab MR fetch, IID extraction, discussion inspection, direct link handling, and resolved-vs-unresolved thread handling.
- Read `gitlab-mr-comment-analysis` next for grouped unresolved-comment analysis, status tracking, stale-file cleanup, and final-report workflow.
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
2. Use `gitlab` to:
   - read the MR overview and comment threads with `glab`
   - inspect structured discussion data with `glab api` when needed
   - extract and reuse the MR IID consistently
   - preserve MR links and direct comment links
   - distinguish resolved vs unresolved threads and actionable vs non-actionable comments
3. Use `gitlab-mr-comment-analysis` to:
   - read the MR overview and comment threads with `glab`
   - group actionable unresolved comments into `work_plan_mr_<MR>.md`
   - track comment links, statuses, analysis file links, and plan history
   - ignore resolved comments and non-actionable chatter
   - remove stale prior-run `analysis_mr_<MR>_*.md` and `mr_<MR>_comment_report.md` files
   - produce the final consolidated report scaffold
4. For each grouped issue in `work_plan_mr_<MR>.md`, use `repository-technical-analysis` plus `private-service-technical-analysis` to inspect the relevant local code, tests, and nearby modules before concluding.
5. After the technical analysis is complete for a grouped issue, run `private-service-contributor` to add concrete proposed changes to the same analysis file.
6. If subagents are explicitly authorized, use `multi-spawn-agent` and spawn one worker per independent grouped issue or per small disjoint set of grouped issues.
7. If subagents are not authorized, analyze the grouped issues sequentially with the same file layout.
8. Finish with the `gitlab-mr-comment-analysis` final report flow and show an on-screen report with 2-3 lines per analyzed grouped issue plus the path to its Markdown file.

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
Use gitlab-mr-comment-analysis, multi-spawn-agent, repository-technical-analysis, private-service-technical-analysis, and private-service-contributor.

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
- use the GitLab skill's stale-file cleanup flow
- create or refresh `mr_<MR>_comment_report.md`
- show a screen summary with 2-3 lines per comment and the corresponding Markdown path
```

## Reporting

Follow the reporting structure from `gitlab-mr-comment-analysis`, but make sure each per-issue analysis adds:

- a private-service-specific technical analysis
- a verdict grounded in local code and test inspection
- a proposed changes section produced with `private-service-contributor`
- any repo-specific prerequisites, environment gaps, or follow-up checks that materially affect the conclusion

## Useful Repo Anchors

- `AGENTS.md` for repo workflow rules
- `Makefile` for standard commands
- `pyproject.toml` for pytest markers and project config
- `cicd/scripts/set_weaviate_config.sh` when analysis depends on production Weaviate settings
