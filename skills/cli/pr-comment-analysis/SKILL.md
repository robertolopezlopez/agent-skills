---
name: cli-pr-comment-analysis
description: Analyze unresolved GitHub PR threads in any Snyk-owned repository from a PR number, URL, or grouped artifact; produce code-grounded verdicts and proposed fixes.
---

# Snyk PR Comment Analysis

Enrich grouped unresolved comments inside the single main PR artifact. Fetch via `GITHUB-ACCESS.md`; never create per-issue artifacts.

## When to Use

Use when a Snyk-owned repository's PR threads need local code analysis. For plain PR/comment fetch, use `GITHUB-ACCESS.md` and `gh`. Do not use without GitHub PR context.

## When Not to Use

Do not use for plain fetches, non-Snyk repositories, or requests without GitHub PR context.

## Inputs

Prefer: existing `$ARTIFACTS/<meaningful_id>/{review,analysis}_pr_<PR>.md` with grouped sections; normalized PR context; then raw PR number/URL.

## First Read

Read `AGENTS.md`, `GITHUB-ACCESS.md`, `github-pr-comment-analysis`, existing main artifact, and `repository-technical-analysis`. For CLI repositories, also load `cli-technical-analysis` and `cli-contributor`; otherwise use the repository's applicable contributor skill.

## Workflow

1. Work from the Snyk repository root. On every requested refresh, update normalized PR context, comments, and commits, then apply `github-pr-comment-analysis` reconciliation so newly resolved issues move automatically from `## Grouped unresolved comments` to `## Resolved threads`.
2. For each `### issue_*`, inspect relevant packages with `repository-technical-analysis` and any applicable repository overlay; write verdict, risks, and prerequisites inside that subsection.
3. Record proposed diffs/commands using the applicable contributor skill, tests first for regressions.
4. Use optional Slack only when PR, code, and Jira lack referenced rationale, incident, rollout, or customer context. Follow `cli-technical-analysis` search/thread flow; record query, channel/date, short redacted snippet, and confirmed vs suggestive status in the issue subsection. Skip when unnecessary/unavailable.
5. If `multi-spawn-agent` is explicitly authorized, give workers disjoint `### issue_*` ownership; never edit one subsection concurrently.
6. Return one action line per thread group and the full main-artifact path.

## Validation

- Cite files, tests, or configs for conclusions; prefer declared `package.json` commands.
- Record Slack search anchors and distinguish confirmed from speculative conclusions.
- Set artifact header to `Analysis date: YYYY-MM-DD` and `Analyzed commit: <full PR head SHA>` from normalized context; local SHA is valid only when equal.

## Outputs / Artifacts

Enrich only the main `$ARTIFACTS/<meaningful_id>/{review,analysis}_pr_<PR>.md` grouped subsections; extend legacy root file only when already active. Return one action line per thread group and the full path.

## Companion Skills

`GITHUB-ACCESS.md`, `github-pr-comment-analysis`, `repository-technical-analysis`, applicable repository contributor/analysis overlays, optional Slack, and authorized `multi-spawn-agent`.

## Safety Notes

Never post to GitHub without explicit request. Redact secrets/customer data. If Slack is unavailable/auth fails, continue without it; never request full exports.
