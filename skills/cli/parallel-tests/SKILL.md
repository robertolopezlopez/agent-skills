---
name: cli-parallel-tests
description: Run broad CLI tests, local CI, or pre-merge validation using documented package/Turbo scripts; parallelize independent commands only when workers are authorized and analyze failures.
---

# CLI Broad Tests

Run wide validation, not one targeted test.

## When to Use

Use for all tests, local CI, pre-merge validation, or broad failure triage. For one package/file, run the narrow command with `tdd`. Do not parallelize without user authorization.

## When Not to Use

Do not use outside CLI or for one targeted test.

## First Read

- Read `AGENTS.md`, any supplied artifact, `package.json` scripts, and `turbo.json` when present.
- Use only documented install and validation commands.

## Workflow

1. From repo root, install dependencies with documented lockfile flow.
2. Pick one or two documented primary drivers. Prefer one canonical test/CI command; split only when distinct scripts exist.
3. With authorized parallelism, give workers disjoint script ownership. Otherwise run sequentially in documented dependency order.
4. Capture command, exit, failing tests, and relevant stderr.
5. Analyze failures with `repository-technical-analysis` plus `cli-technical-analysis`.
6. Preserve confirmed `Frequent Failure Clusters` or `CI Parity Gaps` in durable notes.

## Validation

- Before local splitting, run `scripts/check_skill_prereqs.sh parallel-tests`. If GNU `parallel` is missing, ask with helper's OS-specific install suggestion; on decline, run sequentially.
- Match CI scripts and documented Node/pnpm versions (`.node-version`, `packageManager`).

## Outputs / Artifacts

Return console-ready suite results and optional analysis-artifact links.

## Companion Skills

`cli-technical-analysis`, `repository-technical-analysis`, and `cli-contributor` for fixes.

## Safety Notes

Never publish or run destructive scripts without explicit request. Redact secrets from logs/artifacts.
