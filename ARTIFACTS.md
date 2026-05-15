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
- GitHub PR review bootstrap: `review_pr_<number>.md`
- GitHub PR investigation bootstrap: `analysis_pr_<number>.md`

**Grouped MR/PR comment analysis** lives **inside** the corresponding review or analysis artifact under:

- `## Grouped unresolved comments`
- stable subsections `### issue_01`, `### issue_02`, …

Legacy split filenames (older workflows) may still appear in checkouts and validators:

- `work_plan_mr_<iid>.md`, `analysis_mr_<iid>_issue_<nn>.md`, `mr_<iid>_comment_report.md`
- `work_plan_pr_<number>.md`, `analysis_pr_<number>_issue_<nn>.md`, `pr_<number>_comment_report.md`

Prefer merging durable content from legacy files into the main artifact, then deleting the splits once merged.

## Content Rules

- Keep artifacts local-only unless the user explicitly asks to publish or copy them elsewhere.
- Prefer concise bullets over long prose.
- Keep links canonical and direct when possible.
- Use live Jira/GitLab/GitHub data as source of truth when refreshing artifact contents.
- Treat the artifact as durable working context, not as authority over remote state.

## Skill Responsibilities

- `jira` bootstraps `task_<issue>.md`
- `gitlab` bootstraps `review_mr_<iid>.md` or `analysis_mr_<iid>.md`
- `gitlab-mr-comment-analysis` refreshes live MR state and writes grouped unresolved threads **into** `review_mr_<iid>.md` or `analysis_mr_<iid>.md` (subsections under `## Grouped unresolved comments`)
- `github` prepares normalized PR context; bootstrap filenames such as `review_pr_<number>.md` follow this schema when written locally
- `github-pr-comment-analysis` refreshes live PR state and writes grouped unresolved threads **into** `review_pr_<number>.md` or `analysis_pr_<number>.md` (same subsection contract)
- repository-specific overlay skills should reuse these artifacts when possible instead of recreating context
