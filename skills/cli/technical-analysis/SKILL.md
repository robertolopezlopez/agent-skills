---
name: cli-technical-analysis
description: Investigate CLI TypeScript/JavaScript root causes, regressions, architecture, or performance using pnpm/Turbo-aware repros, CI parity, artifacts, and optional Slack context.
---

# CLI Technical Analysis

Apply CLI-specific evidence over `repository-technical-analysis`.

## When to Use

Use for investigation-first CLI work involving package scripts, entrypoints, packaged binaries, SDK boundaries, or analysis artifacts. When the request names a Jira issue, use its linked-issue context before forming a technical hypothesis. Do not use outside the repo or for transport-only requests.

## When Not to Use

Do not use outside CLI or for transport-only work without local code analysis.

## First Read

- Read `AGENTS.md`, root `README.md`/`CONTRIBUTING.md`, `package.json`, and existing task/review/analysis artifact.
- Load `repository-technical-analysis`; use `circleci` only when evidence lives there.

## Workflow

1. Confirm root and package manager from repo metadata.
2. If a Jira key is provided, or appears in the task/artifact, load `JIRA-ACCESS.md` and fetch the anchor issue with `acli`. By default use `max_depth=1`: enumerate and fetch only its direct parent/epic, child, blocker/blocked-by, relates-to, duplicate, and clone links, preserving link direction, status, summary, description, comments, and acceptance criteria. Do not recursively fetch links from linked issues unless the user explicitly requests a deeper depth. Deduplicate keys and record the fetched key set plus any inaccessible issue as an explicit gap. For example, `CLI-1899` must expand and explain direct links such as `CLI-1732` and `CLI-1679`, not merely cite them.
3. Read the existing task/review/analysis artifact and use the issue graph as investigation anchors.
4. Choose smallest declared test/lint/typecheck repro; use filtered Turbo for cross-package behavior.
5. Capture cwd, exact command, exit, and decisive logs.
6. For acceptance failures, suggest documented `TEST_SNYK_IGNORE_LIST` only for blocking out-of-scope specs, never CLI regressions.
7. Follow documented installed/project CLI config precedence; redact secrets.
8. Write durable fastest repro, false leads, and CI gaps to `$ARTIFACTS/<meaningful_id>/analysis_<name>.md`; use `$KNOWLEDGE/analysis_<name>.md` only for general reference. Extend existing files.
9. Use any connected Slack capability only when local code, CI, Jira, and GitHub are insufficient and team/incident context is relevant; never assume runtime-specific tool names. Search by ticket/PR/error/subsystem/person, resolve named people, then read promising threads. Cite channel, date, short redacted evidence, and confirmed vs suggestive status. Skip and state why when unnecessary or unavailable.
10. For approved code changes, after validation inspect full diff, remove out-of-scope/debug/redundant code without dropping required tests or cross-package fixes, then rerun changed validation.

## Validation

- Re-run smallest repro after hypothesis changes when practical.
- Match CI job scripts when visible.
- Record Slack queries and evidence certainty when used.

## Outputs / Artifacts

Start reports with `Analysis date: YYYY-MM-DD` and `Analyzed commit: <full git SHA>` from `git rev-parse HEAD`.

In artifacts and on-screen output, link every `PR #<number>` reference. Use the existing review artifact when it is the active evidence source; otherwise use the canonical GitHub PR URL from normalized context. Resolve repository identity rather than guessing from the PR number.

## Companion Skills

`repository-technical-analysis` (required), `JIRA-ACCESS.md` + `acli` for issue context, `circleci` for CI facts, `diagnose` for concrete failures, and optional Slack after local/bundled evidence.

## Safety Notes

Never expose credentials or request full Slack exports. Stop when reproduction needs undisclosed auth/signing material; continue without Slack when unavailable.
