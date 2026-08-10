---
name: cli-pr-comment-analysis
description: Analyze unresolved CLI GitHub PR threads from a PR number, URL, or grouped artifact; produce code-grounded verdicts and proposed fixes using CLI analysis/contributor workflows.
---

# CLI PR Comment Analysis

Enrich grouped unresolved comments inside the single main PR artifact. Fetch via `GITHUB-ACCESS.md`; never create per-issue artifacts.

## When to Use

Use when CLI PR threads need local code analysis. For plain PR/comment fetch, use `GITHUB-ACCESS.md` and `gh`. Do not use outside the CLI repo or without GitHub PR context.

## When Not to Use

Do not use for plain fetches, non-CLI work, or requests without GitHub PR context.

## Inputs

Prefer: existing `$ARTIFACTS/<meaningful_id>/{review,analysis}_pr_<PR>.md` with grouped sections; normalized PR context; then raw PR number/URL.

## First Read

Read `AGENTS.md`, `GITHUB-ACCESS.md`, `github-pr-comment-analysis`, existing main artifact, and paired `repository-technical-analysis` plus `cli-technical-analysis`. Use `cli-contributor` for patches/proposed responses.

## Workflow

1. Work from CLI repo root. Refresh normalized PR context and `## Grouped unresolved comments` when stale/missing.
2. For each `### issue_*`, inspect relevant packages with both analysis skills; write verdict, risks, and prerequisites inside that subsection.
3. Record proposed diffs/commands using `cli-contributor`, tests first for regressions.
4. Use optional Slack only when PR, code, and Jira lack referenced rationale, incident, rollout, or customer context. Follow `cli-technical-analysis` search/thread flow; record query, channel/date, short redacted snippet, and confirmed vs suggestive status in the issue subsection. Skip when unnecessary/unavailable.
5. If `multi-spawn-agent` is explicitly authorized, give workers disjoint `### issue_*` ownership; never edit one subsection concurrently.
6. Return short summary and full main-artifact path.

## Validation

- Cite files, tests, or configs for conclusions; prefer declared `package.json` commands.
- Record Slack search anchors and distinguish confirmed from speculative conclusions.
- Set artifact header to `Analysis date: YYYY-MM-DD` and `Analyzed commit: <full PR head SHA>` from normalized context; local SHA is valid only when equal.

## Outputs / Artifacts

Enrich only the main `$ARTIFACTS/<meaningful_id>/{review,analysis}_pr_<PR>.md` grouped subsections; extend legacy root file only when already active. Return per-thread summary and full path.

## Companion Skills

`GITHUB-ACCESS.md`, `github-pr-comment-analysis`, `repository-technical-analysis`, `cli-technical-analysis`, `cli-contributor`, optional Slack, and authorized `multi-spawn-agent`.

## Safety Notes

Never post to GitHub without explicit request. Redact secrets/customer data. If Slack is unavailable/auth fails, continue without it; never request full exports.
