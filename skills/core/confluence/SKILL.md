---
name: confluence
description: Fetch, summarize, search, create, or update Confluence pages/spaces from URLs or IDs; prefer authenticated `acli confluence`, use Basic-auth REST helpers as fallback, and MCP last.
---

# Confluence Access

Prefer authenticated `acli confluence`; fall back to local REST helpers, then MCP. Return normalized page or space data.

## When to Use

Use for Confluence page/space reads, search, summaries, requested create/update operations, or auth diagnosis.

## When Not to Use

Do not use for Jira workitems or unrelated websites.

## Inputs

- Confluence wiki URL or page ID.
- Search/list criteria or requested page content/change.
- Optional API root override and JSON body for helper writes.

## Workflow

1. Run `scripts/check_skill_prereqs.sh confluence` and `scripts/check_skill_config.sh confluence`. Check `acli confluence auth status` first; when unauthenticated, help the user run `acli confluence auth login` before using fallback credentials.
2. Use `acli confluence` when it supports the operation. For a page read, prefer `acli confluence page view --id <ID> --body-format storage --json`.
3. If ACLI is unavailable, its authentication cannot be completed, or it does not support the operation, resolve `scripts/confluence-api` or `scripts/confluence-request` relative to this skill. Helpers use Basic auth and own runtime URL/token resolution; never read defaults files directly unless debugging was requested.
4. Use `confluence-api` for one page and `confluence-request` for arbitrary REST v2 operations. Summarize JSON, not HTML login responses.
5. Use Confluence/Atlassian MCP only when neither ACLI nor the Basic-auth REST helpers can perform the operation; preserve the same normalized result.
6. Read [references/commands.md](references/commands.md) only for exact ACLI auth, helper syntax, config precedence, or create/update flow.

## Validation

- Preserve transport order: authenticated ACLI, Basic-auth REST helpers, then MCP.
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
