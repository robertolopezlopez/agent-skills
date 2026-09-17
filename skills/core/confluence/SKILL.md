---
name: confluence
description: Fetch, summarize, search, create, or update Confluence pages/spaces from URLs or IDs; use `twg confluence`, then ACLI, REST helpers, and MCP.
---

# Confluence Access

Use `twg confluence`; fall back to authenticated ACLI, local REST helpers, then MCP. Return normalized page or space data.

## When to Use

Use for Confluence page/space reads, search, summaries, requested create/update operations, or auth diagnosis.

## When Not to Use

Do not use for Jira workitems or unrelated websites.

## Inputs

- Confluence wiki URL or page ID.
- Search/list criteria or requested page content/change.
- Optional API root override and JSON body for helper writes.

## Workflow

1. Use `twg confluence`. Before an unfamiliar or consequential write, run `twg help describe "confluence <path>"`; use `$HOME/.local/bin/twg` only when `twg` is not on `PATH`.
2. If TWG is unavailable or cannot perform the operation, run `scripts/check_skill_prereqs.sh confluence` and `scripts/check_skill_config.sh confluence`, then use authenticated `acli confluence` when it supports the operation.
3. If ACLI is unavailable, unauthenticated, or unsupported, resolve `scripts/confluence-api` or `scripts/confluence-request` relative to this skill. Use `confluence-api` for one page and `confluence-request` for arbitrary REST v2 operations.
4. Use Confluence/Atlassian MCP only when the local transports cannot perform the operation.
5. Read [references/commands.md](references/commands.md) only for exact commands, fallback configuration, or create/update flow.

## Validation

- Preserve transport order: TWG, authenticated ACLI, Basic-auth REST helpers, then MCP.
- Route fallback HTTP through bundled scripts, never ad hoc Python or raw `curl`.
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
