# Artifact Schema

This repository uses a shared Markdown schema for locally bootstrapped workflow artifacts.

## Goals

- keep Jira, GitLab, GitHub, and follow-on analysis artifacts easy to read
- make downstream skills reuse existing context instead of rebuilding it
- standardize headings, ordering, and file naming without changing skill-specific behavior

## Canonical Core Sections

Bootstrapped task or review artifacts should keep this core order when present:

1. `# Task`
2. `## Summary`
3. `## Type`
4. `## Repository`
5. `## Context Links`
6. `## Selected Skills`
7. `## Defaults Files`
8. `## Assumptions`
9. `## Initial Plan`
10. `## Validation Plan`
11. `## Open Questions`
12. domain-specific details section, such as:
    - `## Jira Details`
    - `## GitLab Details`
    - `## GitHub Details`
13. `## Description`
14. `## Actionable Context`

Downstream workflow files may add extra sections after these, but they should preserve the core sections above when they bootstrap or enrich the same artifact.

## Naming

Preferred file names:

- Jira issue bootstrap: `task_<issue>.md`
- GitLab MR review bootstrap: `review_mr_<iid>.md`
- GitLab MR investigation bootstrap: `analysis_mr_<iid>.md`
- GitLab grouped comment plan: `work_plan_mr_<iid>.md`
- Per-issue MR analysis: `analysis_mr_<iid>_issue_<nn>.md`
- Consolidated MR report: `mr_<iid>_comment_report.md`
- GitHub PR review bootstrap: `review_pr_<number>.md`
- GitHub PR investigation bootstrap: `analysis_pr_<number>.md`
- GitHub grouped comment plan: `work_plan_pr_<number>.md`
- Per-issue PR analysis: `analysis_pr_<number>_issue_<nn>.md`
- Consolidated PR report: `pr_<number>_comment_report.md`

## Content Rules

- Keep artifacts local-only unless the user explicitly asks to publish or copy them elsewhere.
- Prefer concise bullets over long prose.
- Keep links canonical and direct when possible.
- Use live Jira/GitLab/GitHub data as source of truth when refreshing artifact contents.
- Treat the artifact as durable working context, not as authority over remote state.

## Skill Responsibilities

- `jira` bootstraps `task_<issue>.md`
- `gitlab` bootstraps `review_mr_<iid>.md` or `analysis_mr_<iid>.md`
- `gitlab-mr-comment-analysis` consumes MR bootstrap artifacts, refreshes live MR state, and writes grouped issue outputs
- `github` prepares normalized PR context; bootstrap filenames such as `review_pr_<number>.md` follow this schema when written locally
- `github-pr-comment-analysis` consumes PR bootstrap artifacts, refreshes live PR state, and writes grouped issue outputs
- repository-specific overlay skills should reuse these artifacts when possible instead of recreating context
