# confluence

Setup and usage notes for the generic `confluence` skill.

## Purpose

Agents use this skill to access **Confluence Cloud** through the REST API when browser flows hit login walls or API access is more reliable.

Configuration for fallback helpers lives in the runtime **`atlassian.env`** file (**`~/.cursor/atlassian.env`** for Cursor installs, **`~/.codex/atlassian.env`** for Codex). The **`jira`** skill uses the same file. See **AGENTS.md** for runtime detection.

## Files

- `SKILL.md`: skill definition and workflow
- `README.md`: local setup and helper usage
- `scripts/confluence-api`: fetch one page by id with optional query string
- `scripts/confluence-request`: generic Confluence REST v2 request helper

Atlassian authentication lives in the repository manifest **shared_files** helper (`atlassian-auth.sh` next to `validate_artifact.py` under each skills install root). Sync this repository per **AGENTS.md** so that file is present.

## Local Defaults File

Use the runtime **`atlassian.env`** for your install. Bundled helpers read it; agents should invoke helpers instead of opening the file directly.

Example using site URL (helpers append `/wiki/rest/api/v2`):

```bash
ATLASSIAN_API_BASE_URL=https://example.atlassian.net
```

Example using an explicit Confluence REST v2 root:

```bash
ATLASSIAN_CONFLUENCE_API_BASE_URL=https://example.atlassian.net/wiki/rest/api/v2
```

Precedence:

1. explicit helper arguments (full API root URL as first argument)
2. exported environment variables
3. runtime **`atlassian.env`** (loaded by helpers)

Prefer keeping `ATLASSIAN_API_TOKEN` out of these files; export it or use the token file fallback documented below.

## Recommended Setup

Set either:

- `ATLASSIAN_API_BASE_URL` to the Atlassian Cloud site URL (`https://example.atlassian.net`), or
- `ATLASSIAN_CONFLUENCE_API_BASE_URL` to the full REST v2 root (`https://example.atlassian.net/wiki/rest/api/v2`)

Also set `ATLASSIAN_API_TOKEN`.

Auth uses:

- `git config user.email` as the Atlassian username (email)
- `ATLASSIAN_API_TOKEN` as the password for Basic auth with email

If `ATLASSIAN_API_TOKEN` is not exported, the shared auth helper can fall back to:

```text
${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}
```

It reads the first line as the token.

Helpers source the shared Atlassian auth helper from the manifest **shared_files** directory next to `validate_artifact.py` under the skills install root (sync per **AGENTS.md** after cloning or updating).

## Helper usage

### confluence-api

- `confluence-api PAGE_ID`, using defaults from env / `atlassian.env`
- `confluence-api CONFLUENCE_API_ROOT PAGE_ID`
- optional third argument: query string without a leading `?` (default: `body-format=storage`)

### confluence-request

- `confluence-request METHOD PATH [JSON_BODY_FILE]`, using resolved API root from env / `atlassian.env`
- `confluence-request CONFLUENCE_API_ROOT METHOD PATH [JSON_BODY_FILE]` for a one-off root override

Paths are relative to the REST v2 root, for example `/pages/123456789`, `/spaces`, `/pages` for create operations.

Examples:

```bash
scripts/confluence-api 123456789

scripts/confluence-request GET /spaces

scripts/confluence-request POST /pages /tmp/new-page.json
```

## Skill prompts

Examples:

```text
Fetch Confluence page id 123456789 and summarize the storage format body
```

```text
Use confluence-request to GET /spaces and list space keys and names
```

```text
Draft a Confluence page update JSON for title and body, then apply it with confluence-request after confirmation
```

Codex and Cursor should not issue raw Confluence `curl` commands; use MCP when configured, otherwise these helpers.
