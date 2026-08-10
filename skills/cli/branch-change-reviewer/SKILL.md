---
name: cli-branch-change-reviewer
description: >-
  Review CLI product branch diffs with branch-change-reviewer, CLI monorepo evidence,
  caveman-review findings, and a separate ponytail-review simplification pass. Use for read-only
  CLI reviews covering regressions, architecture, package boundaries, CI, tests, and excess code.
---

# CLI Branch Change Reviewer

Apply CLI evidence and terse findings over `branch-change-reviewer`; inherit its scope, artifacts, parallelism, and safety.

## When to Use

Use for CLI repository branch reviews. For PR-thread grouping alone, use `cli-pr-comment-analysis`; do not use for implementation.

## When Not to Use

Do not use outside CLI, for implementation, or for PR-thread grouping without branch review.

## First Read

Load `branch-change-reviewer`, `cli-technical-analysis`, `caveman-review`, and `ponytail-review`. Load `github-pr-comment-analysis` only when unresolved PR comments are in scope.

## Workflow

1. Follow `branch-change-reviewer` end to end.
2. If PR comments are included, refresh grouped unresolved threads with `github-pr-comment-analysis` and use its main PR artifact; create no parallel review artifact.
3. Apply `cli-technical-analysis` to changed packages and affected callers.
4. Run `ponytail-review` on changed production code. Keep simplification findings separate and without bug severities.
5. If parallel review is authorized, split independent CLI packages/surfaces; every worker uses `cli-technical-analysis` and `caveman-review`.
6. Preserve base report structure. Format ordinary findings as:

   ```text
   - High — packages/foo/src/bar.ts:L42: 🔴 bug: null result reaches `email`. Guard before access.
   ```

7. Add `Simplification Findings` using exact `ponytail-review` format; end with its net-lines metric or `Lean already. Ship.` Use fuller prose only when security or architecture needs rationale.

## Validation

Use base checks plus the smallest relevant package/Turbo command selected by `cli-technical-analysis`. Formatting never replaces evidence.

## Outputs / Artifacts

Use base outputs. Start reports with `Analysis date: YYYY-MM-DD` and `Analyzed commit: <full git SHA>` for reviewed HEAD.

## Companion Skills

`branch-change-reviewer`, `cli-technical-analysis`, `repository-technical-analysis`, optional `github-pr-comment-analysis`, `caveman-review`, `ponytail-review`, and authorized `multi-spawn-agent`.

## Safety Notes

Inherit base safety. Never expose tokens or CLI credentials.
