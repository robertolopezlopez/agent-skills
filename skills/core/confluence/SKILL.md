---
name: confluence
description: Fetch, summarize, create, and update Confluence Cloud pages and related resources through the Confluence REST API. Use when the user provides a Confluence wiki URL or page id, asks to read or summarize a page, create or edit wiki content, list spaces, search Confluence, debug Confluence API access using ATLASSIAN_API_TOKEN, or override the Confluence API host and path. Prefer bundled `confluence-api` and `confluence-request` helpers, then Confluence or Atlassian MCP when local helpers are insufficient.
---

# Confluence Wiki Access

When Confluence content is not readable through normal browser access, use the bundled Confluence REST helper workflow first, then Confluence or Atlassian MCP when local helpers are insufficient, before concluding the content is inaccessible.

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
- an optional Confluence API root URL for helper overrides
- JSON bodies for create or update operations when using helpers

## Workflow

1. Invoke bundled helpers for reads and writes. They resolve defaults in this order:
   - exported environment variables (`ATLASSIAN_CONFLUENCE_API_BASE_URL`, then `ATLASSIAN_API_BASE_URL`)
   - then the runtime **`atlassian.env`** file for the active install (see **Local Defaults File**)
   - **Do not read defaults files with the editor/Read tool** unless the user explicitly asked to debug helper resolution.
3. Use `ATLASSIAN_CONFLUENCE_API_BASE_URL` when the full Confluence REST v2 root is known, for example `https://example.atlassian.net/wiki/rest/api/v2`.
4. Otherwise use `ATLASSIAN_API_BASE_URL` as the Atlassian Cloud site URL such as `https://example.atlassian.net`; helpers append `/wiki/rest/api/v2` automatically.
5. Use `git config user.email` as the Atlassian username for helper auth.
6. Use `ATLASSIAN_API_TOKEN` for helper auth. Resolution order (handled by **`atlassian-auth.sh`** — agents do not need to `source` the defaults file):
   - exported **`ATLASSIAN_API_TOKEN`**
   - first line of **`${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}`**
   - **`ATLASSIAN_API_TOKEN`** in runtime **`atlassian.env`** (resolve with **`scripts/agent_config.py --atlassian-env`**)
7. Resolve `scripts/confluence-api` and `scripts/confluence-request` relative to this skill directory.
8. Ensure manifest **shared_files** from this repository have been synced into the active skills install root so the Atlassian auth helper expected by `confluence-api` and `confluence-request` exists under that root `scripts/` directory next to `validate_artifact.py` when missing (follow **AGENTS.md** sync rules). The helpers locate and source that file automatically.
9. If a helper is not executable, run `chmod +x` on the resolved helper path.
10. For page reads, prefer `confluence-api` for a single page id with default storage body format.
11. For arbitrary Confluence REST v2 calls, use `confluence-request` with method and path relative to the resolved API root (paths such as `/pages/{id}`, `/spaces`, `/pages` for create).
12. If the helper request fails due to sandbox network restrictions, rerun the same helper command with escalated network access.
13. Summarize from helper API JSON, not from an HTML login response.
14. Use Confluence or Atlassian MCP only when local helpers are missing or insufficient.
15. Never issue a direct Confluence `curl` command from the skill workflow. Route HTTP through `confluence-api` or `confluence-request`, then MCP when helpers are insufficient.

## Validation

- Run **`scripts/check_skill_config.sh confluence`** (and **`check_skill_prereqs.sh confluence`** for optional `jq`). If Atlassian defaults or auth are missing, **help the user** finish **`atlassian.env`** setup (shared with **`jira`**) per **AGENTS.md**.
- Bundled **`confluence-api`** / **`confluence-request`** are required; sync shared files per **AGENTS.md** if helpers are missing from the install root.
- Prefer bundled helpers before Confluence or Atlassian MCP.
- Keep helper execution routed through `confluence-api` or `confluence-request`, never direct `curl`.
- Resolve auth and base URL defaults before invoking helpers.

## Transport Preference

Preferred order:

1. `confluence-api` for single-page reads by id
2. `confluence-request` for arbitrary REST v2 operations
3. Confluence or Atlassian MCP when local helpers are missing or insufficient

## API reference cache

Resolve **`$AGENT_CONFIG_HOME/api-docs/confluence-rest-v2/`** with **`scripts/agent_config.py --api-docs-dir confluence-rest-v2`**.

1. Read the cached `README.md` and endpoint notes when present.
2. On first use (or when stale), fetch or summarize [Confluence Cloud REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/) docs into that directory — especially page read/write and space endpoints used by `confluence-api` / `confluence-request`.
3. On later uses, consult the cache before re-downloading docs.

See **AGENTS.md** (REST API reference cache).

## Helper Source

The canonical page-read helper lives at `scripts/confluence-api`, resolved relative to this skill directory.
The canonical generic request helper lives at `scripts/confluence-request`, resolved relative to this skill directory.
Atlassian authentication and runtime config resolution are shared with the `jira` skill through repository manifest **shared_files** helpers (`atlassian-auth.sh`, `agent-config.sh` under each skills install root `scripts/` directory). Do not duplicate that logic inline in helpers.

## Local Defaults File

Bundled helpers load defaults from **one** runtime config home (see **AGENTS.md**). Resolve the active file with **`scripts/agent_config.py --atlassian-env`** (or **`scripts/agent-config.sh --atlassian-env`**).

Override detection with **`AGENT_SKILLS_RUNTIME=cursor`** or **`codex`**, or set **`AGENT_CONFIG_HOME`**.

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
- let **`confluence-api`** / **`confluence-request`** read the runtime defaults file for URLs and token; agents must not open the file unless debugging config resolution
- **`ATLASSIAN_API_TOKEN`** may live in **`atlassian.env`** when not exported; prefer export or the credentials file when your environment already provides them

## Shell Helper Commands

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

- same Atlassian auth conventions as the `jira` skill (`git config user.email`; token from env, credentials file, or runtime **`atlassian.env`** via **`atlassian-auth.sh`**)
- base URL defaults from exported env vars or the runtime **`atlassian.env`** file loaded by helpers, unless overridden

### Generic flow

1. Infer draft title, space, parent page id, and body format from the user request.
2. Confirm destructive or wide-reaching edits before executing writes.
3. Build JSON payloads matching [Confluence REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/) expectations and call `confluence-request`. Use MCP only when helpers are insufficient.
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
- If `ATLASSIAN_API_TOKEN` is already exported, helpers do not read the credentials file or **`atlassian.env`** for the token.
- If auth works but content is still unavailable, report that the account likely lacks Confluence permission for that space or page.
