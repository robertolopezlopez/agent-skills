---
name: cli-technical-analysis
description: >-
  Investigate the CLI product repository with repository-technical-analysis, pnpm/Turbo-aware
  repro commands, CI parity, artifact conventions, and optional Slack context. Use for CLI
  TypeScript/JavaScript root-cause, regression, architecture, or performance analysis.
---

# CLI Technical Analysis

Apply CLI-specific evidence over `repository-technical-analysis`.

## When to Use

Use for investigation-first CLI work involving package scripts, entrypoints, packaged binaries, SDK boundaries, or analysis artifacts. Do not use outside the repo or for transport-only requests.

## When Not to Use

Do not use outside CLI or for transport-only work without local code analysis.

## First Read

- Read `AGENTS.md`, root `README.md`/`CONTRIBUTING.md`, `package.json`, and existing task/review/analysis artifact.
- Load `repository-technical-analysis`; use `circleci` only when evidence lives there.

## Workflow

1. Confirm root and package manager from repo metadata.
2. Choose smallest declared test/lint/typecheck repro; use filtered Turbo for cross-package behavior.
3. Capture cwd, exact command, exit, and decisive logs.
4. For acceptance failures, suggest documented `TEST_SNYK_IGNORE_LIST` only for blocking out-of-scope specs, never CLI regressions.
5. Follow documented installed/project CLI config precedence; redact secrets.
6. Write durable fastest repro, false leads, and CI gaps to `$ARTIFACTS/<meaningful_id>/analysis_<name>.md`; use `$KNOWLEDGE/analysis_<name>.md` only for general reference. Extend existing files.
7. Use any connected Slack capability only when local code, CI, Jira, and GitHub are insufficient and team/incident context is relevant; never assume runtime-specific tool names. Search by ticket/PR/error/subsystem/person, resolve named people, then read promising threads. Cite channel, date, short redacted evidence, and confirmed vs suggestive status. Skip and state why when unnecessary or unavailable.
8. For approved code changes, after validation inspect full diff, remove out-of-scope/debug/redundant code without dropping required tests or cross-package fixes, then rerun changed validation.

## Validation

- Re-run smallest repro after hypothesis changes when practical.
- Match CI job scripts when visible.
- Record Slack queries and evidence certainty when used.

## Outputs / Artifacts

Start reports with `Analysis date: YYYY-MM-DD` and `Analyzed commit: <full git SHA>` from `git rev-parse HEAD`.

## Companion Skills

`repository-technical-analysis` (required), `circleci` for CI facts, `diagnose` for concrete failures, and optional Slack after local/bundled evidence.

## Safety Notes

Never expose credentials or request full Slack exports. Stop when reproduction needs undisclosed auth/signing material; continue without Slack when unavailable.
