---
name: confluence
description: Fetch, summarize, search, create, and update Confluence Cloud pages and spaces from wiki URLs or IDs. Prefer authenticated `acli confluence`, then bundled `confluence-api`/`confluence-request`, then Confluence or Atlassian MCP. Use for Confluence content work and access diagnosis.
---

# Confluence Access

Use local CLI/helpers as the transport boundary; return normalized page or space data.

## When to Use

Use for Confluence page/space reads, search, summaries, requested create/update operations, or auth diagnosis.

## When Not to Use

Do not use for Jira workitems or unrelated websites.

## Inputs

- Confluence wiki URL or page ID.
- Search/list criteria or requested page content/change.
- Optional API root override and JSON body for helper writes.

## Workflow

1. Run `scripts/check_skill_prereqs.sh confluence` and `scripts/check_skill_config.sh confluence`. Prefer authenticated `acli confluence`; help finish one supported setup path before fallback.
2. Use `acli confluence` when it supports the operation. For a page read, prefer `acli confluence page view --id <ID> --body-format storage --json`.
3. Otherwise resolve `scripts/confluence-api` or `scripts/confluence-request` relative to this skill. Helpers own runtime URL/token resolution; never read defaults files directly unless debugging was requested.
4. Use `confluence-api` for one page and `confluence-request` for arbitrary REST v2 operations. Summarize JSON, not HTML login responses.
5. Use Confluence/Atlassian MCP only when local transports cannot perform the operation; preserve the same normalized result.
6. Read [references/commands.md](references/commands.md) only for exact helper syntax, config precedence, or create/update flow.

## Validation

- Prefer the narrowest supported local command.
- Route helper HTTP through bundled scripts, never raw `curl`.
- Stop clearly on auth/permission failures without exposing tokens.
- For uncertain fields or endpoints, consult the runtime `confluence-rest-v2` cache per `AGENTS.md`.

## Outputs / Artifacts

Return requested page title/ID/space/version/body excerpt, collection summaries, canonical URLs, or concise access diagnosis. For writes, return the resulting page ID and URL.

## Companion Skills

Use `repository-technical-analysis` when wiki context leads into code investigation.

## Safety Notes

- Read-only unless the user explicitly requests a write.
- Confirm destructive, production, broad, or ambiguous edits.
- Fetch the current version before updates; preserve optimistic-lock semantics.
- Never expose tokens or duplicate shared Atlassian auth logic.
