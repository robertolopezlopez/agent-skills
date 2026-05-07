---
name: confluence
description: Fetch, summarize, create, and update Confluence Cloud pages and related resources through the Confluence REST API. Use when the user provides a Confluence wiki URL or page id, asks to read or summarize a page, create or edit wiki content, list spaces, search Confluence, debug Confluence API access using ATLASSIAN_API_TOKEN, or override the Confluence API host and path. Prefer Confluence or Atlassian MCP when available, with bundled helper fallback.
---

# Confluence Wiki Access

When Confluence content is not readable through normal browser access, prefer Confluence or Atlassian MCP when available, otherwise use the bundled Confluence REST helper workflow before concluding the content is inaccessible.

## When to Use

Use this skill when the user wants to:

- fetch or summarize a Confluence page
- create or update a Confluence page (title, body, parent, space)
- list spaces or navigate space metadata
- run Confluence REST v2 reads or writes that fit the generic helper pattern
- debug Confluence helper access or Atlassian auth defaults for wiki operations

## When Not to Use

Do not use this skill when:

- the task is Jira issue access only (use `jira`)
- the task is GitLab MR access or Git repository context
- the task is only local documentation editing with no live Confluence access

## Inputs

Accept, depending on the requested action:

- a Confluence wiki URL (browser URL containing `/wiki/`)
- a numeric page id when using REST v2 directly
- a space key or resource identifiers required by the chosen API operation
- an optional Confluence API root URL for fallback helper overrides
- JSON bodies for create or update operations when using fallback helpers

## Workflow

1. Prefer Confluence or Atlassian MCP for reads and writes when a suitable MCP server is configured in the session.
2. Resolve defaults for fallback helpers in this order:
   - exported environment variables (`ATLASSIAN_CONFLUENCE_API_BASE_URL`, then `ATLASSIAN_API_BASE_URL`)
   - then the first readable defaults file (**`~/.cursor/atlassian.env`**, then **`~/.codex/atlassian.env`**)
3. Use `ATLASSIAN_CONFLUENCE_API_BASE_URL` when the full Confluence REST v2 root is known, for example `https://example.atlassian.net/wiki/rest/api/v2`.
4. Otherwise use `ATLASSIAN_API_BASE_URL` as the Atlassian Cloud site URL such as `https://example.atlassian.net`; helpers append `/wiki/rest/api/v2` automatically.
5. Use `git config user.email` as the Atlassian username for fallback helper auth.
6. Use `ATLASSIAN_API_TOKEN` from the environment as the fallback helper password.
   - If it is unset, the shared auth helper may fall back to `${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}` and read the first line as the token.
   - Prefer the environment variable when available.
7. Resolve `scripts/confluence-api` and `scripts/confluence-request` relative to this skill directory for fallback helper use.
8. Ensure manifest **shared_files** from this repository have been synced into the active skills install root so the Atlassian auth helper expected by `confluence-api` and `confluence-request` exists under that root `scripts/` directory next to `validate_artifact.py` when missing (follow **AGENTS.md** sync rules). The helpers locate and source that file automatically.
9. If a helper is not executable, run `chmod +x` on the resolved helper path.
10. For page reads without MCP, prefer `confluence-api` for a single page id with default storage body format.
11. For arbitrary Confluence REST v2 calls without MCP, use `confluence-request` with method and path relative to the resolved API root (paths such as `/pages/{id}`, `/spaces`, `/pages` for create).
12. If the fallback helper request fails due to sandbox network restrictions, rerun the same helper command with escalated network access.
13. Summarize from MCP output when available, otherwise from the fallback API JSON, not from an HTML login response.
14. Never issue a direct Confluence `curl` command from the skill workflow. All Confluence HTTP access must go through Confluence or Atlassian MCP when available, otherwise through `confluence-api` or `confluence-request`.

## Validation

- Prefer Confluence or Atlassian MCP first when available.
- Keep fallback helper execution routed through `confluence-api` or `confluence-request`, never direct `curl`.
- Resolve auth and base URL defaults before invoking fallback helpers.

## Transport Preference

Preferred order:

1. Confluence or Atlassian MCP for reads, creates, updates, and structured wiki operations
2. `confluence-api` for fallback single-page reads by id
3. `confluence-request` for fallback arbitrary REST v2 operations

## Helper Source

The canonical page-read helper lives at `scripts/confluence-api`, resolved relative to this skill directory.
The canonical generic request helper lives at `scripts/confluence-request`, resolved relative to this skill directory.
Atlassian authentication behavior is shared with the `jira` skill through the repository manifest **shared_files** helper (same `scripts/` directory as `validate_artifact.py` under each skills install root). Do not duplicate that logic inline in helpers.

Use **`~/.cursor/atlassian.env`** first, then **`~/.codex/atlassian.env`**, for non-secret defaults; keep tokens out of those files unless the local environment explicitly requires it.

## Local Defaults File

If `~/.cursor/atlassian.env` or `~/.codex/atlassian.env` exists, read the first match for each variable in that order before invoking fallback helpers.

Preferred usage:

```bash
ATLASSIAN_API_BASE_URL=https://example.atlassian.net
```

Optional explicit Confluence root (skips automatic `/wiki/rest/api/v2` suffix):

```bash
ATLASSIAN_CONFLUENCE_API_BASE_URL=https://example.atlassian.net/wiki/rest/api/v2
```

Rules:

- treat explicit helper arguments as highest priority
- treat exported environment variables as higher priority than defaults files
- use **`~/.cursor/atlassian.env`**, then **`~/.codex/atlassian.env`**, for defaults, not for required per-request overrides
- prefer keeping `ATLASSIAN_API_TOKEN` in the environment or existing credentials flow instead of storing it in a defaults file

## Fallback Command Pattern

Single page read (default query `body-format=storage`):

```bash
<resolved-path-to-scripts/confluence-api> {PAGE_ID}
```

Explicit API root before page id:

```bash
<resolved-path-to-scripts/confluence-api> https://example.atlassian.net/wiki/rest/api/v2 {PAGE_ID}
```

Custom query string after page id (omit leading `?`; concatenated as `?{QUERY}`):

```bash
<resolved-path-to-scripts/confluence-api> {PAGE_ID} body-format=storage
```

Generic REST request:

```bash
<resolved-path-to-scripts/confluence-request> GET /pages/{PAGE_ID}
```

```bash
<resolved-path-to-scripts/confluence-request> POST /pages /tmp/create-page.json
```

Explicit API root:

```bash
<resolved-path-to-scripts/confluence-request> https://example.atlassian.net/wiki/rest/api/v2 PUT /pages/{PAGE_ID} /tmp/update-page.json
```

## Outputs / Artifacts

Return normalized results for the task, such as:

- page title, id, space id, version metadata, and body excerpt or format requested
- created or updated page id and wiki URL when available from the response
- lists of spaces or other collection summaries
- helper or auth diagnosis

## Create and Update Workflow

Use this workflow when the user asks to publish or revise wiki content.

### Prerequisites

- same Atlassian auth conventions as the `jira` skill (`git config user.email`, `ATLASSIAN_API_TOKEN`, optional token file fallback)
- base URL defaults from **`~/.cursor/atlassian.env`**, then **`~/.codex/atlassian.env`**, unless overridden

### Generic flow

1. Infer draft title, space, parent page id, and body format from the user request.
2. Confirm destructive or wide-reaching edits before executing writes.
3. Prefer MCP for create and update. If MCP is unavailable or insufficient, build JSON payloads matching [Confluence REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/) expectations and call `confluence-request`.
4. Use separate calls when the workflow requires fetching the current page version before an update (optimistic locking via version numbers).
5. Report back page id and canonical wiki URL when present in API responses.

## Companion Skills

Use this skill as the Confluence transport layer.

Common pairings:

- `repository-technical-analysis` when investigation starts from remote wiki context or needs evidence-backed follow-up in a codebase

## Safety Notes

- Never issue direct Confluence `curl` commands from this skill.
- Keep shared Atlassian auth behavior in vendored helper scripts instead of duplicating it inline.
- Do not expose the raw token in outputs.
- Confirm before overwriting production pages or space-wide changes.

## Notes

- Prefer concise summaries unless the user asks for detail.
- Resolve helper paths relative to this skill directory instead of relying on `PATH`.
- If `ATLASSIAN_API_TOKEN` is already set, do not probe `~/.config/.jira/.credentials` just to verify auth.
- If auth works but content is still unavailable, report that the account likely lacks Confluence permission for that space or page.
