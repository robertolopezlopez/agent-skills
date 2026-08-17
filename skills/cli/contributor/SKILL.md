---
name: cli-contributor
description: Implement CLI TypeScript/JavaScript monorepo changes with TDD, Ponytail scope control, documented package scripts, pnpm/Turbo scoping, injectable design, CI-aligned validation, and MR summaries.
---

# CLI Contributor

Apply CLI repository rules over `tdd`, `repository-technical-analysis`, and `ponytail`.

## When to Use

Use for CLI repository implementation/fixes. Do not use outside the repo or for transport-only tasks without code changes.

## When Not to Use

Do not use outside CLI or for read-only transport with no local change.

## First Read

- Read root `AGENTS.md`, relevant existing artifact, and `package.json`; inspect workspace/Turbo files when present. Never invent scripts.
- Load `tdd`, `repository-technical-analysis`, `ponytail`, and synced `LITERAL-CODE-SEARCH.md`; use `circleci` only for CI context. If Ponytail is unavailable, suggest installing its plugin for the active runtime, do not install without explicit approval, then continue and report the gap.

## Design Principles

- Inject collaborators through constructors, parameters, or explicit context/factories; avoid deep singleton imports.
- Keep mutable state/config out of module globals and wire it at CLI entrypoints or tests.
- Keep I/O at edges; make core logic testable with fakes instead of broad mock trees.
- For behavior/regressions, use `tdd` red-green-refactor through public interfaces.

## Workflow

1. Follow documented package manager; prefer pnpm only when repo metadata does.
2. Choose the narrowest declared lint/typecheck/test/build script. Use filtered Turbo only for cross-package work.
3. Use optional Slack only when code, artifacts, Jira, and GitHub lack needed design/review/rollout/repro context. Follow `cli-technical-analysis` search/thread procedure; cite channel, date, short redacted evidence, and whether confirmed or suggestive. Skip cleanly when unavailable.
4. Validate relevant packages. Run declared lint and typecheck after substantive edits; use CI-equivalent scripts when names match.
5. For acceptance failures, suggest documented `TEST_SNYK_IGNORE_LIST` only for blocking specs outside CLI scope, never CLI regressions.
6. Before finishing, use `ponytail` to review the full diff; preserve required tests and cross-package fixes, then rerun validation if production code changed.
7. Follow `ARTIFACTS.md`: read existing context first, refresh against current code/CI, extend existing artifacts, and preserve schema.

## Git Staging and Commits

- Stage only durable tests that add necessary, non-redundant regression protection. Keep diagnostic, refactoring-only, or build/package-automation-redundant tests in the local working tree and out of Git; do not add ignore rules solely to hide them.
- When commits are requested for multiple independent features, fixes, or optimizations, make one functional commit per task. Include its necessary tests and explain why the change exists in each commit message.

## Merge Request Summaries

1. Compare committed branch changes against agreed base, default `origin/main`.
2. Use matching `.gitlab/merge_request_templates/` template when present and complete every section.
3. Explain what/why; link known work. Include risk, rollout, Slack evidence, or follow-ups only when grounded in diff/discussion.

## Validation

Record commands, exits, and relevant failures. Stop and ask when required auth, tokens, or signing are missing.

## Outputs / Artifacts

Return repo-local command/validation choices and, when requested, completed MR description. Update artifacts only when task needs them.

## Companion Skills

`tdd`, `ponytail`, `diagnose`, `repository-technical-analysis`, `cli-technical-analysis`, and `circleci` as needed.

## Safety Notes

Never invent scripts or expose secrets. If Slack is unavailable/auth fails, continue without it; never request full exports.
