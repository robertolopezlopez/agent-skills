# confluence

Setup and usage notes for the generic `confluence` skill.

## Purpose

Agents use this skill to access **Confluence Cloud** through the REST API when browser flows hit login walls or API access is more reliable.

Configuration for fallback helpers lives in the runtime **`atlassian.env`** file for the active install. Resolve it with **`scripts/agent_config.py --atlassian-env`**. The **`jira`** skill uses the same file. See **AGENTS.md** for runtime detection.

Check readiness:

```bash
~/.cursor/skills/scripts/check_skill_config.sh confluence
```

If setup is incomplete, help the user using **`templates/atlassian.env.example`** and **AGENTS.md** (runtime tool and helper configuration).

## Files

- `SKILL.md`: skill definition and workflow
- `README.md`: local setup and helper usage
- `scripts/confluence-api`: fetch one page by id with optional query string
- `scripts/confluence-request`: generic Confluence REST v2 request helper

Atlassian authentication lives in the repository manifest **shared_files** helper (`atlassian-auth.sh` next to `validate_artifact.py` under each skills install root). Sync this repository per **AGENTS.md** so that file is present.

## Local Defaults File

Use the runtime defaults file for your install. Resolve the path with **`scripts/agent_config.py --atlassian-env`**. Bundled helpers read URLs and **`ATLASSIAN_API_TOKEN`** from it when not exported; agents should invoke helpers instead of opening the file directly.

Example:

```bash
ATLASSIAN_API_BASE_URL=https://example.atlassian.net
# ATLASSIAN_API_TOKEN=...   # optional; also supported via export or ~/.config/.jira/.credentials
```

Precedence:

1. explicit helper arguments
2. exported environment variables
3. runtime **`atlassian.env`** (loaded by helpers for URLs and token)

See **`templates/atlassian.env.example`** in the agent-skills repository.

Example using an explicit Confluence REST v2 root:

```bash
ATLASSIAN_CONFLUENCE_API_BASE_URL=https://example.atlassian.net/wiki/rest/api/v2
```

## Recommended Setup

Set either:

- `ATLASSIAN_API_BASE_URL` to the Atlassian Cloud site URL (`https://example.atlassian.net`), or
- `ATLASSIAN_CONFLUENCE_API_BASE_URL` to the full REST v2 root (`https://example.atlassian.net/wiki/rest/api/v2`)

Also set `ATLASSIAN_API_TOKEN` (export, credentials file, or runtime **`atlassian.env`**).

Auth uses:

- `git config user.email` as the Atlassian username (email)
- `ATLASSIAN_API_TOKEN` as the password for Basic auth with email (resolved by **`atlassian-auth.sh`**)

If `ATLASSIAN_API_TOKEN` is not exported, the shared auth helper falls back to:

```text
${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}
```

then runtime **`atlassian.env`**. It reads the first line of the credentials file as the token.

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

Codex and Cursor should not issue raw Confluence `curl` commands; use `confluence-api` and `confluence-request` first, then Confluence or Atlassian MCP when helpers are insufficient.
