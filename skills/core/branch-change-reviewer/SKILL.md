---
name: branch-change-reviewer
description: Review the current branch against a target Git branch, defaulting to origin/main, and write review findings to a Markdown output file under `$ARTIFACTS/{meaningful_id}/` (default basename `review_{sanitized-branch}.md`; legacy root-level review files remain valid). For non-trivial diffs, use authorized read-only parallel workers through multi-spawn-agent. Use when Codex is asked to review a branch diff without writing code, especially to assess code style, architecture, testing, regressions, and whether changes are worth raising as comments.
---

# Branch Change Reviewer

Review a branch diff without changing code. Report only actionable findings to
both the screen and a Markdown artifact.

## When to Use

- Branch-diff review for regressions, architecture, tests, or maintainability
- Written review artifact requested or useful

## When Not to Use

- Implementation or fix requests
- MR transport or comment-grouping work
- Broad investigation without a branch diff

## Inputs

- Target branch; default `origin/main`.
- Optional output path. Otherwise resolve
  `$ARTIFACTS/<meaningful_id>/review_<sanitized-branch>.md`; use a provided
  tracker key as `meaningful_id`, else the branch slug.
- Optional workflow artifact for context.
- Optional parallel preference. Explicit `$branch-change-reviewer` invocation
  authorizes its documented read-only workers; ask before workers when the
  skill was activated implicitly.
- Reuse an existing user or legacy root-level review path instead of moving it.

## Workflow

1. Read repository guidance that affects review standards.
2. Run `git status --short --branch`, identify the current branch, fetch the
   target, and resolve the output path per `ARTIFACTS.md`.
3. Read relevant workflow and prior review artifacts before repeating work.
4. Review committed changes first. Include relevant uncommitted changes
   explicitly when present.
5. Read changed and adjacent files. When impact is unclear, follow
   `LITERAL-CODE-SEARCH.md` to inspect callers, contracts, renames, and shared
   helpers.
6. Use parallel review below when authorized and worthwhile.
7. Verify findings against the live diff, then write the final report.

## Parallel Review

- Keep small or tightly coupled diffs local.
- For non-trivial diffs, create a temporary work-definition file containing
  target, scope, changed files, worker assignments, and constraints. Never
  replace an existing review artifact with temporary coordination content.
- Spawn 2–3 read-only workers with context forking enabled. Split by disjoint
  file groups when practical; otherwise by correctness, architecture, and
  tests. The main agent remains the only report writer.
- Tell each worker to read the work definition, use
  `branch-change-reviewer` plus relevant analysis skills, inspect only its
  scope, make no edits, and say: `You are not alone in the codebase; do not
  revert others' changes.`
- Require file-and-line evidence, scope reviewed, validation run, and blockers.
  Continue a non-overlapping local review before waiting.
- Verify and deduplicate worker findings against the live diff, then remove the
  temporary work definition.

## Review Standards

- Prioritize bugs, regressions, architectural drift, missing or incorrect
  tests, and maintainability problems worth raising.
- Check callers, data flows, contracts, edge cases, and existing behavior.
- Treat missing tests as a finding only when changed behavior lacks equivalent
  coverage.
- Flag duplicated logic, weakened boundaries, or coupling that conflicts with
  established patterns.
- Raise style only when it materially harms readability or maintenance.
- Prefer concrete file and line references. Do not invent risks without
  evidence.
- Record `Missed In Prior Review` only when a newly visible risk has a concrete
  signal that should have been checked earlier.

## Validation

- Ground every finding in the current diff and surrounding code.
- Run or inspect the smallest relevant checks when they materially change
  confidence.
- Keep findings concise and severity-ordered.

## Outputs / Artifacts

Write identical review content to the screen and output file:

1. `Findings`, ordered by severity. Include location, issue, impact, and fix or
   verification for each finding.
2. `Open Questions` only when they affect the verdict.
3. Evidence-backed learned sections when useful.
4. `Summary` naming current branch, target, whether target was defaulted,
   output path, and whether findings exist.

Always create the file, including when no findings warrant comments.

## Prior Artifacts

On reruns, preserve still-valid `Recurring Findings`, `Missed In Prior Review`,
and `Repo-Specific Review Heuristics`; refresh findings from live code and
remove stale heuristics. Preserve shared sections required by `ARTIFACTS.md`.

## Companion Skills

- `multi-spawn-agent` for authorized parallel review
- Repository-specific analysis overlays when the diff needs them

## Safety Notes

- Do not modify code, tests, or configuration.
- Do not apply fixes or rewrite user files.
- Keep existing user changes intact.
- Do not let praise or minor style points hide material findings.
