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

## Artifact directories

Prefer writing **new** artifacts under the repository root:

```text
_artifacts_/<meaningful_id>/<basename>.md
```

### `meaningful_id`

Pick a compact, filesystem-safe label so parallel work separates cleanly:

1. **Tracker key first** — e.g. `CLI-123`, `GOV-456`.
2. **Else PR / MR shorthand** — e.g. `pr-336`, `mr-1447`.
3. **Else** a sanitized slug from the git branch (`feature/foo-bar` → `feature-foo-bar`) or a topic slug the user provides.

Use the **same `meaningful_id` for every file** belonging to one ticket/session when possible.

### Precedence

Resolution order:

1. **Explicit user instruction** — absolute or relative paths always win for that run.
2. **Repo `AGENTS.md` or project rules** — may pin a canonical pattern (always use Jira keys, hyphen rules, prefix per team).
3. **Heuristic** — tracker key → PR/MR id → branch/topic slug as above.

### Backward compatibility

- Existing artifacts **at repo root** (or elsewhere) remain valid. Open and extend them instead of relocating unless the user asks to migrate.
- **New bootstrap or analysis sessions** prefer `_artifacts_/<meaningful_id>/` paths so generated files cluster under one subdirectory per work item.

### Git hygiene

- Treat `_artifacts_/` as local working state unless the team chooses otherwise; add `_artifacts_/` (or narrower patterns beneath it) to `.gitignore` only when artifacts must not ship (common default).

## Naming

**Basenames** (under `_artifacts_/<meaningful_id>/`):

- Jira issue bootstrap: `task_<issue>.md`
- GitLab MR review bootstrap: `review_mr_<iid>.md`
- GitLab MR investigation bootstrap: `analysis_mr_<iid>.md`
- GitHub PR review bootstrap: `review_pr_<number>.md`
- GitHub PR investigation bootstrap: `analysis_pr_<number>.md`
- Repository / branch investigations: existing patterns such as `analysis_<relevant_name>.md` or `review_<sanitized-branch>.md` — place them under `_artifacts_/<meaningful_id>/` unless the artifact already exists elsewhere

Equivalent paths at repo root are still tolerated for legacy workflows; `_artifacts_/...` remains the preference for newly created files.

Full examples:

- `_artifacts_/CLI-123/task_CLI-123.md`
- `_artifacts_/mr-1447/review_mr_1447.md`
- `_artifacts_/pr-336/review_pr_336.md`
- `_artifacts_/feature-auth-guard/review_feature-auth-guard.md` (branch-based branch review layouts)

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

- `jira` bootstraps `task_<issue>.md` under `_artifacts_/<meaningful_id>/` (`meaningful_id` defaults to issue key unless overridden)
- `gitlab` bootstraps `review_mr_<iid>.md` or `analysis_mr_<iid>.md` under `_artifacts_/<meaningful_id>/` (`meaningful_id` defaults sensibly — e.g. `mr-<iid>` unless the repo dictates otherwise)
- `gitlab-mr-comment-analysis` refreshes live MR state and writes grouped unresolved threads **into** the main MR Markdown file (typically `_artifacts_/…/review_mr_<iid>.md` or `_artifacts_/…/analysis_mr_<iid>.md`) inside `## Grouped unresolved comments`
- `github` prepares normalized PR context; bootstrap filenames such as `review_pr_<number>.md` follow this schema when written locally, defaulting beneath `_artifacts_/<meaningful_id>/` for new artifacts
- `github-pr-comment-analysis` refreshes live PR state and writes grouped unresolved threads **into** the canonical PR Markdown file (typically `_artifacts_/…/review_pr_<number>.md` or `_artifacts_/…/analysis_pr_<number>.md`) under the same subsection contract
- repository-specific overlay skills should reuse these artifacts when possible instead of recreating context
